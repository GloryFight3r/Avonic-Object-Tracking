import socket
import binascii
import time

class Camera:
    """
    This class contains camera information and methods to interact directly with the camera.
    """
    sock = None
    address = None

    def __init__(self, sock:socket.socket, address):
        """ Constructor for Camera

        Args:
            address (): ip and port in the format (ip, port)
            sock: socket.socket in the format (socket.AF_INET, socket.SOCK_STREAM)
        """
        self.sock = sock #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address #('192.168.5.93', 1259) # 1259 is the default port for TCP
        self.sock.connect(self.address)

    def __del__(self):
        """ Destructor for the current object
            Closes the TCP connection
        """
        self.sock.close()

    def reconnect(self):
        time.sleep(1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.address)

    def send_no_response(self, header:str, command:str, data:str) -> None:
        """ Sends the reboot command to the camera, but does not wait for a response

        Args:
            header:
            command:
            data:
        """
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        data = bytes.fromhex(data)
        message = header + command + data + bytes([sum(header + command + data) & 0xFF])

        self.sock.sendall(message)

    def send(self, header:str, command:str, data:str) -> bytes:
        """ Sends the current command to the camera using the visca protocol

        Args:
            header: header for the current command
            command: the command the camera has to execute in accordance to the visca protocol
            data: data that is specific to the current command

        Returns:
            Response code from the camera
        """
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        data = bytes.fromhex(data)
        message = header + command + data + bytes([sum(header + command + data) & 0xFF])

        self.sock.sendall(message)

        data2 = self.sock.recv(2048)

        return binascii.hexlify(data2).upper()
