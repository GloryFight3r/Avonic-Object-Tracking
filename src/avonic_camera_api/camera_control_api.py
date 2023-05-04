from avonic_camera_api.camera_adapter import Camera
import binascii

class CameraAPI:
    def __init__(self, camera:Camera):
        """Constructor for cameraAPI

        Args:
            camera: object of type Camera
        """
        self.camera = camera

    def reboot(self) -> None:
        """ Reboots the camera - the camera will do a complete reboot

        Returns:
            The response code from the camera
        """
        msg = self.camera.send_no_response('', '81 0A 01 06 01 FF', '')

        self.camera.reconnect()

        return None

    def stop(self) -> bytes:
        """ Stops the camera from rotating

        Returns:
            The response code from the camera
        """
        return self.camera.send('', '81 01 06 01 05 05 03 03 FF', '')

    def turn_on(self) -> bytes:
        """ Turns on the camera

        Returns:
            The response code from the camera
        """
        return self.camera.send('', '81 01 04 00 02 FF', '')

    def turn_off(self) -> bytes:
        """ Turns off the camera - the camera continues receiving and responding to requests

        Returns:
            The response code from the camera
        """
        return self.camera.send('', '81 01 04 00 03 FF', '')

    def home(self) -> bytes:
        """ Points the camera towards the 'home' direction

        Returns:
            The response code from the camera
        """
        return self.camera.send('', '81 01 06 04 FF', '')
    
    def degrees_to_command(self, degree:float) -> str:
        """Transforms an angle in degree to a command code for visca call

        Args:
            degree: an angle in degrees, can be a float but precision could be lost

        Returns:
            A byte code that will be used for a visca command call
        """
        degree_divided = int(degree / 0.0625)

        if (degree_divided < 0):
            degree_divided = ((abs(degree_divided) - 1) ^ ((1 << 16) - 1))

        in_bytes = hex(degree_divided)[2:]
        
        in_bytes = '0' * (4 - len(in_bytes)) + in_bytes
        
        answer_string = ''

        for t in in_bytes:
            answer_string += '0' + t

        return answer_string

    def move_relative(self, speedX:int, speedY:int, degreesX:float, degreesY:float) -> bytes:
        """Rotates the camera relative to the current rotation degree

        Args:
            speedX: Integer in the range [0x01(hex) : 0x18(hex)] indicating the pan speed
            speedY: Integer in the range [0x01(hex) : 0x14(hex)] indicating the tilt speed
            degreesX: Pan position, could be a float but precision might be lost - range is [-170° ~ +170°] 
            degreesY: Tilt position, could be a float but precision might be lost - range is [-30° to +90°]
        Returns:
            The response code from the camera
        """
        assert speedX > 0 and speedX <= 24 and speedY > 0 and speedY <= 20
        assert degreesX >= -170 and degreesX <= +170 and degreesY >= -30 and degreesY <= +90

        return self.camera.send('', '81 01 06 03' + str(speedX.to_bytes(1, 'big').hex()) + " " + str(speedY.to_bytes(1, 'big').hex()) + " " + self.degrees_to_command(degreesX) + " " + self.degrees_to_command(degreesY) + " FF", '')

    def move_absolute(self, speedX:int, speedY:int, degreesX:float, degreesY:float) -> bytes:
        """Rotates the camera in absolute position(current possition does not matter)

        Args:
            speedX: Integer in the range [0x01(hex) : 0x18(hex)] indicating the pan speed
            speedY: Integer in the range [0x01(hex) : 0x14(hex)] indicating the tilt speed
            degreesX: Pan position, could be a float but precision might be lost - range is [-170° ~ +170°] 
            degreesY: Tilt position, could be a float but precision might be lost - range is [-30° to +90°]

        Returns:
            The response code from the camera
        """
        assert speedX > 0 and speedX <= 24 and speedY > 0 and speedY <= 20
        assert degreesX >= -170 and degreesX <= +170 and degreesY >= -30 and degreesY <= +90

        return self.camera.send('', '81 01 06 02' + str(speedX.to_bytes(1, 'big').hex()) + " " + str(speedY.to_bytes(1, 'big').hex()) + " " + self.degrees_to_command(degreesX) + " " + self.degrees_to_command(degreesY) + " FF", '')

    def get_zoom(self):
        """Get the camera zoom as an int between 0x0000 and 0x0400.

            Returns:
                zoom_value (int): The value of zoom between 0 (min) and 16384 (max)
        """
        message = "81 09 04 47 FF"

        self.camera.send_no_response('', message, '')
        ret = str(binascii.hexlify(self.camera.sock.recv(2048)).upper())[2:-1].split("FF")
        print(ret)
        ret = list(filter(lambda x : len(x) == 12, ret))
        while len(ret) == 0:
            ret = str(binascii.hexlify(self.camera.sock.recv(2048)).upper())[2:-1].split("FF")
            ret = list(filter(lambda x : len(x) == 12, ret))
        ret = ret[0] + "FF"
        print(len(ret))
        print(ret)
        print("DAS")
        assert len(ret) == 14
        
        hex_res = ret[7] + ret[9] + ret[11] + ret[13]
        return int(hex_res, 16)

    def direct_zoom(self, zoom: int) -> None:
        """
        Change the value of the zoom to the specified value.

            Parameters:
                value (int): The value of zoom between 0 (min) and 16384 (max)
        """
        assert zoom >= 0 and zoom <= 16384
        message = "81 01 04 47 0p 0q 0r 0s FF"
        final_message = insert_zoom_in_hex(message, zoom)
        self.camera.send('', final_message, '')

def insert_zoom_in_hex(msg: str, zoom: int) -> str:
    """
    Inserts the value of the zoom into the hex string in the right format.

        Parameters:
            hex_str (str): The hex message.
            zoom (int): The value of zoom between 0 (min) and 16384 (max)

        Returns:
            message (str): The hex message with inserted values
    """
    assert zoom >= 0 and zoom <= 16384
    assert len(msg) == 26
    insert = hex(zoom)[2:]
    padded_insert = (4 - len(insert)) * "0" + insert
    p = padded_insert[0]
    q = padded_insert[1]
    r = padded_insert[2]
    s = padded_insert[3]
    res = msg[:13] + p + msg[14:16] + q + msg[17:19] + r + msg[20:22] + s + msg[23:]
    return res
