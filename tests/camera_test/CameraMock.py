from maat_camera_api.camera_control_api import insert_zoom_in_hex
from maat_camera_api.camera_adapter import ResponseCode

class CameraMock:
    """
    Mock camera class to artificially set the zoom value and keep track of amount of requests sent.
    """
    call_count = None
    zoom = None

    def __init__(self, timeout=False):
        self.call_count = 0
        self.zoom = 16384
        self.timeout = timeout

    def send(self, header, command, data):
        if self.timeout:
            return ResponseCode.TIMED_OUT
        if len(command) == 26:
            # to set the zoom of the camera
            hex_res = command[13] + command[16] + command[19] + command[22]
            self.zoom = int(hex_res, 16)

        self.call_count += 1
        message = "81 01 04 47 0p 0q 0r 0s FF"
        ret = insert_zoom_in_hex(message, self.zoom).replace(" ", "")[2:]
        return ret

    def send_no_response(self, header, command, data):
        pass
