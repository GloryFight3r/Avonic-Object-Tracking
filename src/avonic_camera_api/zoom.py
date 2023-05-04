import socket
import binascii

class Camera:
    """
    This class contains camera information and methods to interact directly with the camera.
    """
    sock = None
    address = None

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = ('192.168.5.94', 1259) # 1259 is the default port for TCP
        self.sock.connect(self.address)

    def send(self, header, command, data):
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        data = bytes.fromhex(data)
        message = header + command + data + bytes([sum(header + command + data) & 0xFF])

        self.sock.sendall(message)

        data2 = self.sock.recv(2048)

        return binascii.hexlify(data2).upper()

class CameraAPI:
    """
    The API to communicate with the Avonic camera.
    """
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
        ret = str(self.camera.send('', message, ''))
        hex_res = ret[7] + ret[9] + ret[11] + ret[13]
        print(ret[13])
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
