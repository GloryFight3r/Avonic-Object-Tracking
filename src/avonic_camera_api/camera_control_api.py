from avonic_camera_api.camera_adapter import Camera
import numpy as np
from avonic_camera_api import converter
import binascii


class CameraAPI:
    def __init__(self, camera: Camera):
        """ Constructor for cameraAPI

        Args:
            camera: object of type Camera
        """
        self.camera = camera
        self.counter = 1

    def message_counter(self) -> str:
        cnt_hex = self.counter.to_bytes(1, 'big').hex()

        self.counter += 1

        self.counter %= 256

        return cnt_hex

    def reboot(self) -> None:
        """ Reboots the camera - the camera will do a complete reboot
        """
        self.camera.send_no_response('01 00 00 06 00 00 00' + self.message_counter(), '81 0A 01 06 01 FF')

        self.camera.reconnect()

        return None

    def stop(self) -> bytes:
        """ Stops the camera from rotating

        Returns:
            The response code from the camera
        """
        return self.camera.send('01 00 00 09 00 00 00' + self.message_counter(), '81 01 06 01 05 05 03 03 FF', self.counter)

    def turn_on(self) -> bytes:
        """ Turns on the camera

        Returns:
            The response code from the camera
        """
        return self.camera.send('01 00 00 06 00 00 00' + self.message_counter(), '81 01 04 00 02 FF', self.counter)

    def turn_off(self) -> bytes:
        """ Turns off the camera - the camera continues receiving and responding to requests

        Returns:
            The response code from the camera
        """
        return self.camera.send('01 00 00 06 00 00 00' + self.message_counter(), '81 01 04 00 03 FF', self.counter)

    def home(self) -> bytes:
        """ Points the camera towards the 'home' direction

        Returns:
            The response code from the camera
        """
        return self.camera.send('01 00 00 05 00 00 00' + self.message_counter(), '81 01 06 04 FF', self.counter)

    def degrees_to_command(self, degree: float) -> str:
        """ Transforms an angle in degree to a command code for visca call

        Args:
            degree: an angle in degrees, can be a float but precision could be lost
        Returns:
            A byte code that will be used for a visca command call
        """
        degree_divided = int(degree / 0.0625)

        if degree_divided < 0:
            degree_divided = ((abs(degree_divided) - 1) ^ ((1 << 16) - 1))

        in_bytes = hex(degree_divided)[2:]
        
        in_bytes = '0' * (4 - len(in_bytes)) + in_bytes
        
        answer_string = ''

        for t in in_bytes:
            answer_string += '0' + t

        return answer_string

    def move_relative(self, speed_x: int, speed_y: int, degrees_x: float, degrees_y: float) -> bytes:
        """ Rotates the camera relative to the current rotation degree

        Args:
            speed_x: Integer in the range [0x01(hex) : 0x18(hex)] indicating the pan speed
            speed_y: Integer in the range [0x01(hex) : 0x14(hex)] indicating the tilt speed
            degrees_x: Pan position, could be a float but precision might be lost - range is [-170° ~ +170°]
            degrees_y: Tilt position, could be a float but precision might be lost - range is [-30° to +90°]

        Returns:
            The response code from the camera
        """
        assert 0 < speed_x <= 24 and 0 < speed_y <= 20
        assert -170 <= degrees_x <= +170 and -30 <= degrees_y <= +90

        return self.camera.send('01 00 00 0F 00 00 00' + self.message_counter(), '81 01 06 03' + str(speed_x.to_bytes(1, 'big').hex()) + " " +
                                str(speed_y.to_bytes(1, 'big').hex()) + " " + self.degrees_to_command(degrees_x) + " " +
                                self.degrees_to_command(degrees_y) + " FF", self.counter)

    def move_absolute(self, speed_x: int, speed_y: int, degrees_x: float, degrees_y: float) -> bytes:
        """ Rotates the camera in absolute position (current position does not matter)

        Args:
            speed_x: Integer in the range [0x01(hex) : 0x18(hex)] indicating the pan speed
            speed_y: Integer in the range [0x01(hex) : 0x14(hex)] indicating the tilt speed
            degrees_x: Pan position, could be a float but precision might be lost - range is [-170° ~ +170°]
            degrees_y: Tilt position, could be a float but precision might be lost - range is [-30° to +90°]

        Returns:
            The response code from the camera
        """
        assert 0 < speed_x <= 24 and 0 < speed_y <= 20
        assert -170 <= degrees_x <= +170 and -30 <= degrees_y <= +90

        return self.camera.send('01 00 00 0F 00 00 00' + self.message_counter(), '81 01 06 02' + str(speed_x.to_bytes(1, 'big').hex()) + " " +
                                str(speed_y.to_bytes(1, 'big').hex()) + " " + self.degrees_to_command(degrees_x) + " " +
                                self.degrees_to_command(degrees_y) + " FF", self.counter)

    def move_vector(self, speed_x: int, speed_y: int, vec: [float]) -> bytes:
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

    def get_zoom(self):
        """ Get the camera zoom as an int between 0x0000 and 0x0400.

            Returns:
                zoom_value (int): The value of zoom between 0 (min) and 16384 (max)
        """
        message = "81 09 04 47 FF"

        ret = self.camera.send('01 00 00 05 00 00 00' + self.message_counter(), message, self.counter)
        
        hex_res = ret[7] + ret[9] + ret[11] + ret[13]
        return int(hex_res, 16)

    def direct_zoom(self, zoom: int) -> None:
        """ Change the value of the zoom to the specified value.

            Parameters:
                zoom (int): The value of zoom between 0 (min) and 16384 (max)
        """
        assert 0 <= zoom <= 16384
        message = "81 01 04 47 0p 0q 0r 0s FF"
        final_message = insert_zoom_in_hex(message, zoom)
        self.camera.send('01 00 00 09 00 00 00' + self.message_counter(), final_message, self.counter)


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
