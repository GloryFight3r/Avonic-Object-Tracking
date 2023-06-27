import math
from enum import Enum
import re
from multiprocessing import Value
import numpy as np

from maat_camera_api.camera_adapter import CameraSocket, ResponseCode
from maat_camera_api.camera_http_request import CameraHTTP
from maat_camera_api import converter

PAN_STEP = 341/(2448+2448)
TILT_STEP = 121/(1296+443)


class CompressedFormat(Enum):
    MJPEG = 0
    H264 = 1
    H265 = 2


class ImageSize(Enum):
    P1920_1080 = 0
    P1280_720 = 1


class CameraAPI:
    latest_direction: np.ndarray | None = None

    MIN_FOV = np.array([3.72, 2.14])
    # The FOV of the camera when fully zoomed out
    MAX_FOV = np.array([60.38, 35.80])
    MAX_ZOOM_VALUE = 16384

    def __init__(self, camera: CameraSocket, camera_http: CameraHTTP):
        """ Constructor for cameraAPI

        Args:
            camera: object of type Camera
        """
        self.camera = camera
        self.camera_http = camera_http
        self.counter = Value('i', 1)
        self.video = "on"
        self.latest_direction = np.array([0, 0, 1], dtype='float')

    def set_address(self, new_socket, address=None) -> ResponseCode:
        """ Sets the camera address and establishes the new connection
        """
        if address is None:
            print("WARNING: Camera address not specified!")
            return ResponseCode.NO_ADDRESS
        return self.camera.reconnect(new_socket, address=address)

    def message_counter(self) -> (str, int):
        """ Get current message count
        Increments the count for next message.

        Returns:
            The current message count TODO: and what
        """
        cnt_hex = self.counter.value.to_bytes(1, 'big').hex()

        temp_counter = (self.counter.value + 1) % 256
        self.counter.value = temp_counter

        return cnt_hex, temp_counter

    def reboot(self, new_socket) -> ResponseCode:
        """ Reboots the camera - the camera will do a complete reboot
        """
        hx, cnt = self.message_counter()
        self.camera.send_no_response('01 00 00 06 00 00 00' + hx,
                                     '81 0A 01 06 01 FF')

        response = self.camera.reconnect(new_socket)

        if response == ResponseCode.COMPLETION:
            self.set_camera_codec(CompressedFormat.MJPEG)
            return response
        else:
            return response

    def stop(self) -> ResponseCode | str:
        """ Stops the camera from rotating

        Returns:
            The response code from the camera
        """
        hx, cnt = self.message_counter()
        return self.camera.send('01 00 00 09 00 00 00' + hx,
                                '81 01 06 01 05 05 03 03 FF', cnt)

    def turn_on(self) -> ResponseCode | str:
        """ Turns on the camera

        Returns:
            The response code from the camera
        """
        hx, cnt = self.message_counter()
        res = self.camera.send('01 00 00 06 00 00 00' + hx,
                               '81 01 04 00 02 FF', cnt)
        if res == ResponseCode.ACK:
            self.video = "on"
        return res

    def turn_off(self) -> ResponseCode | str:
        """ Turns off the camera - the camera continues receiving and responding to requests

        Returns:
            The response code from the camera
        """
        hx, cnt = self.message_counter()
        res = self.camera.send('01 00 00 06 00 00 00' + hx,
                               '81 01 04 00 03 FF', cnt)
        if res == ResponseCode.ACK:
            self.video = "off"
        return res

    def home(self) -> ResponseCode | str:
        """ Points the camera towards the 'home' direction
        This means that the vector will be [0, 0, 1], the angles (0, 0)

        Returns:
            The response code from the camera
        """
        hx, cnt = self.message_counter()
        return self.camera.send('01 00 00 05 00 00 00' + hx,
                                '81 01 06 04 FF', cnt)

    def move_relative(self, speed_x: int, speed_y: int,
                      degrees_x: float, degrees_y: float) -> ResponseCode | str:
        """ Rotates the camera relative to the current rotation degree

        Args:
            speed_x: Integer in the range [0x01(hex) : 0x18(hex)] indicating the pan speed
            speed_y: Integer in the range [0x01(hex) : 0x14(hex)] indicating the tilt speed
            degrees_x: Pan position, could be a float but precision might be lost
               range is [-170° ~ +170°]
            degrees_y: Tilt position, could be a float but precision might be lost
               range is [-30° to +90°]

        Returns:
            The response code from the camera
        """
        assert 0 < speed_x <= 24 and 0 < speed_y <= 20
        assert -170 <= degrees_x <= +170 and -30 <= degrees_y <= +90

        hx, cnt = self.message_counter()
        return self.camera.send('01 00 00 0F 00 00 00' + hx,
                                '81 01 06 03' + str(speed_x.to_bytes(1, 'big').hex()) + " " +
                                str(speed_y.to_bytes(1, 'big').hex()) + " " +
                                degrees_to_command(degrees_x, PAN_STEP) + " " +
                                degrees_to_command(degrees_y, TILT_STEP) + " FF", cnt)

    def move_absolute(self, speed_x: int, speed_y: int,
                      degrees_x: float, degrees_y: float) -> ResponseCode | str:
        """ Rotates the camera in absolute position (current position does not matter)

        Args:
            speed_x: Integer in the range [0x01(hex) : 0x18(hex)] indicating the pan speed
            speed_y: Integer in the range [0x01(hex) : 0x14(hex)] indicating the tilt speed
            degrees_x: Pan position, could be a float but precision might be lost
                range is [-170° ~ +170°]
            degrees_y: Tilt position, could be a float but precision might be lost
                range is [-30° to +90°]

        Returns:
            The response code from the camera
        """
        assert 0 < speed_x <= 24 and 0 < speed_y <= 20
        assert -170 <= degrees_x <= +170 and -30 <= degrees_y <= +90

        hx, cnt = self.message_counter()
        return self.camera.send('01 00 00 0F 00 00 00' + hx,
                                '81 01 06 02' + str(speed_x.to_bytes(1, 'big').hex()) + " " +
                                str(speed_y.to_bytes(1, 'big').hex()) +
                                " " + degrees_to_command(degrees_x, PAN_STEP) + " " +
                                degrees_to_command(degrees_y, TILT_STEP) + " FF", cnt)

    def move_vector(self, speed_x: int, speed_y: int, vec: list[float]) -> ResponseCode | str:
        """ Rotates the camera in the direction of a vector (with home position being [0, 0, 1]

        Args:
            speed_x: Integer in the range [0x01(hex) : 0x18(hex)] indicating the pan speed
            speed_y: Integer in the range [0x01(hex) : 0x14(hex)] indicating the tilt speed
            vec: a float array with the length of 3

        Returns:
            The response code from the camera
        """
        angle_x, angle_y = converter.vector_angle(np.array(vec))
        return self.move_absolute(speed_x, speed_y, np.rad2deg(angle_x), np.rad2deg(angle_y))

    def get_zoom(self) -> ResponseCode | int:
        """ Get the camera zoom as an int between 0x0000 and 0x0400.

            Returns:
                zoom_value (int): The value of zoom between 0 (min) and 16384 (max)
        """
        message = "81 09 04 47 FF"

        hx, cnt = self.message_counter()
        ret = self.camera.send('01 00 00 05 00 00 00' + hx,
                               message, cnt)
        if isinstance(ret, ResponseCode):
            return ret
        hex_res = ret[7] + ret[9] + ret[11] + ret[13]
        return int(hex_res, 16)

    def direct_zoom(self, zoom: int) -> ResponseCode | str:
        """ Change the value of the zoom to the specified value.

            Parameters:
                zoom (int): The value of zoom between 0 (min) and 16384 (max)
        """
        assert 0 <= zoom <= 16384
        message = "81 01 04 47 0p 0q 0r 0s FF"
        final_message = insert_zoom_in_hex(message, int(zoom))
        hx, cnt = self.message_counter()
        return self.camera.send('01 00 00 09 00 00 00' + hx,
                                final_message, cnt)

    def get_direction(self) -> np.ndarray | ResponseCode:
        """ Get the direction of the camera as a unit vector.

            Returns:
                The pan and tilt of the camera converted into a unit vector:
                    Pan ranges between 0xF670 (-2447) and 0x0990 (2448)
                        while pan_adjusted ranges between (-170°) and (+170°)
                    Tilt ranges between 0xFE45 (-442) and 0x0510 (1296)
                        while tilt_adjusted ranges between (-30°) and (+90°)
                The vector is a 3D numpy array of three floats.
        """
        message = "81 09 06 12 FF"
        hx, cnt = self.message_counter()
        ret = self.camera.send('01 00 00 05 00 00 00' + hx,
                               message, cnt)
        if isinstance(ret, ResponseCode):
            return ret

        # checks whether the response is in the correct format
        # 90 50 0w 0w 0w 0w 0z 0z 0z 0z FF
        valid = re.compile(r"b'90500[A-F_0-9]0[A-F_0-9]0[A-F_0-9]0[A-F_0-9]0[A-F_0-9]0[A-F_0-9]0[A-F_0-9]0[A-F_0-9]FF'")

        if not valid.match(str(ret)):
            return self.latest_direction

        ret_msg = str(ret)[2:-1]  # remove b' and '
        pan_hex = ret_msg[5] + ret_msg[7] + ret_msg[9] + ret_msg[11]
        tilt_hex = ret_msg[13] + ret_msg[15] + ret_msg[17] + ret_msg[19]

        pan = int(pan_hex, 16)
        tilt = int(tilt_hex, 16)
        pan_adjusted = pan
        tilt_adjusted = tilt
        if ret_msg[5] == "F":
            pan_adjusted = -((pan ^ ((1 << 16) - 1)) + 1)
        if ret_msg[13] == "F":
            tilt_adjusted = -((tilt ^ ((1 << 16) - 1)) + 1)

        pan_rad = pan_adjusted * PAN_STEP / 180 * math.pi
        tilt_rad = tilt_adjusted * TILT_STEP / 180 * math.pi
        direction = converter.angle_vector(pan_rad, tilt_rad)
        self.latest_direction = direction
        return direction

    def set_camera_codec(self, selected: CompressedFormat) -> None:
        """ Set the codec of the camera via HTTP

        Args:
            selected: a codec - MJPEG, H264 or H265
        """
        if selected == CompressedFormat.MJPEG:
            self.camera_http.send(
                '{"SetEnv":{"VideoEncode":[{"stMaster": {"emVideoCodec":1},"nChannel":0}]}}')
        elif selected == CompressedFormat.H264:
            self.camera_http.send(
                '{"SetEnv":{"VideoEncode":[{"stMaster": {"emVideoCodec":5},"nChannel":0}]}}')
        elif selected == CompressedFormat.H265:
            self.camera_http.send(
                '{"SetEnv":{"VideoEncode":[{"stMaster": {"emVideoCodec":7},"nChannel":0}]}}')
        else:
            raise KeyError("No such compression exists")

    def set_image_size(self, selected: ImageSize) -> None:
        """ Set camera image resolution via HTTP

        Args:
            selected: the new resolution, either 1280x720 (HD) or 1920x1080 (Full HD)
        """
        if selected == ImageSize.P1280_720:
            self.camera_http.send(
                '{"SetEnv":{"VideoEncode":[{"stMaster": {"emImageSize":4},"nChannel":0}]}}')
        elif selected == ImageSize.P1920_1080:
            self.camera_http.send(
                '{"SetEnv":{"VideoEncode":[{"stMaster": {"emImageSize":5},"nChannel":0}]}}')

    def set_frame_rate(self, selected: int) -> None:
        """ Set camera frame rate per second via HTTP

        Args:
            selected: the new FPS - 5 <= x <= 60
        """
        assert 5 <= selected <= 60
        self.camera_http.send(
            '{"SetEnv":{"VideoEncode":[{"stMaster": {"nFrameRate":%d},"nChannel":0}]}}' 
            % selected)

    def set_i_frame_rate(self, selected: int):
        """ Set interval between i-Frames (full ones) on the camera via HTTP

        Args:
            selected: the new interval - 1 <= x <= 300,
                      lower - less artifacts, higher quality
                      higher - less network usage
        """
        assert 1 <= selected <= 300
        self.camera_http.send(
            '{"SetEnv":{"VideoEncode":[{"stMaster": {"nIFrameInterval":%d},"nChannel":0}]}}'
            % selected)

    def calculate_fov(self) -> ResponseCode | np.ndarray:
        """ Calculate the current FoV based on the current zoom

            Returns:
                array with the two FoVs [horizontal, vertical]

        """
        current_zoom = self.get_zoom()

        if isinstance(current_zoom, ResponseCode):
            return current_zoom

        assert 0 <= current_zoom <= 16384

        current_fov = self.MAX_FOV - ((self.MAX_FOV - self.MIN_FOV)
                                      * current_zoom / self.MAX_ZOOM_VALUE)

        return current_fov


def degrees_to_command(degree: float, step_size: float) -> str:
    """ Transforms an angle in degree to a command code for VISCA call

    Args:
        degree: an angle in degrees, can be a float but precision could be lost
        step_size: PAN_STEP or TILT_STEP - how many degrees correspond to the
                                           byte number increment
    Returns:
        A byte code that will be used for a VISCA command call
    """
    degree_divided = int(degree / step_size)

    if degree_divided < 0:
        degree_divided = (abs(degree_divided) - 1) ^ ((1 << 16) - 1)

    in_bytes = hex(degree_divided)[2:]

    in_bytes = '0' * (4 - len(in_bytes)) + in_bytes

    answer_string = ''

    for t in in_bytes:
        answer_string += '0' + t

    return answer_string


def insert_zoom_in_hex(msg: str, zoom: int) -> str:
    """ Inserts the value of the zoom into the hex string in the right format.

        Parameters:
            msg (str): The hex message.
            zoom (int): The value of zoom between 0 (min) and 16384 (max)

        Returns:
            message (str): The hex message with inserted values
    """
    assert 0 <= zoom <= 16384
    assert len(msg) == 26
    insert = hex(zoom)[2:]
    padded_insert = (4 - len(insert)) * "0" + insert
    p = padded_insert[0]
    q = padded_insert[1]
    r = padded_insert[2]
    s = padded_insert[3]
    res = msg[:13] + p + msg[14:16] + q + msg[17:19] + r + msg[20:22] + s + msg[23:]
    return res
