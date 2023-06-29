import socket
import binascii
from enum import Enum


class ResponseCode(Enum):
    """
    This enum contains the 9 possible camera response codes.
    """
    ACK = 0
    COMPLETION = 1
    SYNTAX_ERROR = 2
    BUFFER_FULL = 3
    CANCELED = 4
    NO_SOCKET = 5
    NOT_EXECUTABLE = 6
    TIMED_OUT = 7
    NO_ADDRESS = 8


class CameraSocket:
    """
    This class contains camera information and methods to interact directly with the camera.
    """
    sock = None  # low-level C socket
    address = None
    message_dict: dict[int, str] = {}
    response_codes = {
        "b'9041FF'": ResponseCode.ACK,
        "b'9051FF'": ResponseCode.COMPLETION,
        "b'906002FF'": ResponseCode.SYNTAX_ERROR,
        "b'906003FF'": ResponseCode.BUFFER_FULL,
        "b'906104FF'": ResponseCode.CANCELED,
        "b'906105FF'": ResponseCode.NO_SOCKET,
        "b'906141FF'": ResponseCode.NOT_EXECUTABLE
    }

    def __init__(self, sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM), address=None):
        """ Constructor for CameraSocket

        Args:
            sock: a UDP socket
            address: camera IP and port in the format (IP, port)
        """
        self.sock = sock
        if address is None or address == ('0.0.0.0', 52381):
            print("WARNING: Camera address not specified!")
            self.address = ('0.0.0.0', 52381)
            return
        self.address = address
        self.sock.connect(self.address)

    def __del__(self):
        """ Destructor for the current object
            Closes the TCP connection
        """
        try:
            self.sock.close()
        except Exception as e:
            print(e)

    def reconnect(self, sock, address=None):
        """ Re-connect to camera after a reboot
        """
        if address is None or address == ('0.0.0.0', 52381):
            if self.address is None or self.address == ('0.0.0.0', 52381):
                print("WARNING: Camera address not specified!")
                return ResponseCode.NO_ADDRESS
        else:
            self.address = address
        self.sock = sock
        self.sock.settimeout(20.0)
        try:
            self.sock.connect(self.address)
            return ResponseCode.COMPLETION
        except TimeoutError:
            ip, port = self.address
            print("ERROR: Cannot connect to camera on address " + ip + ":" + str(port))
            return ResponseCode.TIMED_OUT

    def send_no_response(self, header: str, command: str) -> None:
        """ Sends the command to the camera, but does not wait for a response

        Args:
            header: header for the current command
            command: the command the camera has to execute in accordance to the VISCA protocol
        """
        if self.address is None or self.address == ('0.0.0.0', 52381):
            print("WARNING: Camera address not specified!")
            return
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        message = header + command

        self.sock.sendall(message)

    def send(self, header: str, command: str, message_counter: int) -> ResponseCode | str:
        """ Sends the current command to the camera using the VISCA protocol

        Args:
            header: header for the current command
            command: the command the camera has to execute in accordance to the VISCA protocol
            message_counter: amount of messages received so far

        Returns:
            Response code from the camera
        """
        if self.address is None or self.address == ('0.0.0.0', 52381):
            print("WARNING: Camera address not specified!")
            return ResponseCode.NO_ADDRESS
        header = bytes.fromhex(header)
        command = bytes.fromhex(command)
        message = header + command

        try:
            self.sock.sendall(message)
            self.sock.settimeout(0.05)
            data = binascii.hexlify(self.sock.recv(2048)).upper()
        except (TimeoutError, OSError):
            return ResponseCode.TIMED_OUT

        while True:
            split_messages = str(data).split("'b'")
            if len(split_messages) > 0:
                split_messages[0] = split_messages[0][2:]

            for x in split_messages[:]:
                # If the message is a completion message, ignore it
                if x[16:][2:4] != '51':
                    self.message_dict[int('0x' + x[14:16], 16)] = "b'" + x[16:]

            if message_counter - 1 in self.message_dict:
                ret = self.message_dict[message_counter - 1]
                del self.message_dict[message_counter - 1]
                if ret in self.response_codes:
                    return self.response_codes[ret]
                return ret
            else:
                self.sock.settimeout(0.05)
                try:
                    data = binascii.hexlify(self.sock.recv(2048)).upper()
                except (TimeoutError, OSError):
                    return ResponseCode.TIMED_OUT
