import socket
import binascii

class Camera:
    sock = None
    address = None

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ('192.168.5.93', 1259)

    def send(self, header, command, data):
        self.sock.connect(self.address)
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        data = bytes.fromhex(data)
        message = header + command + data + bytes([sum(header + command + data) & 0xFF])

        self.sock.sendall(message)

        data2 = self.sock.recv(1024)
        self.sock.close()

        return binascii.hexlify(data2).upper()

class API:
    camera = None

    def __init__(self, camera):
        self.camera = camera

    def get_zoom(self):
        """
        Get the camera zoom as an int between 0x0000 and 0x0400.

            Returns:
                zoom_value (int): The value of zoom between 0 (min) and 16384 (max)
        """
        message = "81 09 04 47 FF"
        ret = str(self.camera.send('', message, ''))[2:-1] # remove b' and '
        hex_res = ret[5] + ret[7] + ret[9] + ret[11]
        return int(hex_res, 16)

    def direct_zoom(self, value):
        """
        Change the value of the zoom to the specified value.

            Parameters:
                value (int): The value of zoom between 0 (min) and 16384 (max)
        """
        message = "8x 01 04 47 0p 0q 0r 0s FF"


def insert_zoom_in_hex(hex_str, zoom):
    """
    Inserts the value of the zoom into the hex string in the right format.

        Parameters:
            hex_str (str): The hex message.
            zoom (int): The value of zoom between 0 (min) and 16384 (max)

        Returns:
            message (str): The hex message with inserted values
    """
    assert zoom > 0 and zoom <= 16384
