import socket
import binascii
import time


class Camera:
    """
    This class contains camera information and methods to interact directly with the camera.
    """
    sock = None
    address = None
    message_dict = dict()

    def __init__(self, sock: socket.socket, address):
        """ Constructor for Camera

        Args:
            address: ip and port in the format (ip, port)
            sock: socket.socket in the format (socket.AF_INET, socket.SOCK_STREAM)
        """
        self.sock = sock  # socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.address = address  # ('192.168.5.93', 1259) # 1259 is the default port for TCP
        self.sock.connect(self.address)

    def __del__(self):
        """ Destructor for the current object
            Closes the TCP connection
        """
        self.sock.close()

    def reconnect(self):
        """ Re-connect to camera after a reboot

        :return:
        """
        time.sleep(1)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.connect(self.address)

    def send_no_response(self, header: str, command: str) -> None:
        """ Sends the reboot command to the camera, but does not wait for a response

        Args:
            header: header for the current command
            command: the command the camera has to execute in accordance to the VISCA protocol
        """
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        message = header + command

        self.sock.sendall(message)

    def send(self, header:str, command:str, message_counter: int) -> bytes:
        """ Sends the current command to the camera using the VISCA protocol

        Args:
            header: header for the current command
            command: the command the camera has to execute in accordance to the VISCA protocol

        Returns:
            Response code from the camera
        """
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        message = header + command 

        self.sock.sendall(message)

        self.sock.settimeout(5.0)
        data2 = binascii.hexlify(self.sock.recv(2048)).upper()

        while True:
            split_messages = str(data2).split("'b'")
            if len(split_messages) > 0:
                split_messages[0] = split_messages[0][2:]

            for x in split_messages[:]:
                if x[16:][2:4] != '51': # its a completion message
                    self.message_dict[int('0x' + x[14:16], 16)] = "b'" + x[16:]

            if message_counter - 1 in self.message_dict:
                ret = self.message_dict[message_counter - 1]
                del self.message_dict[message_counter - 1]
                return ret
            else:
                self.sock.settimeout(5.0)
                data2 = binascii.hexlify(self.sock.recv(2048).upper())
