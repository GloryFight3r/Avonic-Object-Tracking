import socket


class MicrophoneSocket:
    """
    This class contains methods to send and receive raw UDP packets to the microphone.
    """
    def __init__(self, sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM), address=None):
        """ Constructor for Microphone Socket

        Args:
            sock: a UDP socket
            address: the IP and port in the format (IP, port)
        """
        self.sock = sock
        if address is None or address == ('0.0.0.0', 45):
            print("WARNING: Microphone address not specified!")
            self.address = ('0.0.0.0', 45)
            return
        self.address = address

    def __del__(self):
        """ Destructor for Microphone Socket
            Closes UDP connection
        """
        try:
            self.sock.close()
        except:
            pass

    def connect(self, address=None) -> bool:
        if address is None or address == ('0.0.0.0', 45):
            print("WARNING: Microphone address not specified!")
            return False
        self.address = address
        return True

    def send(self, command: str, responses: int = 1) -> list[str]:
        """ Send a command and wait for a response

        Args:
            command: the command in JSON format (refer to
                https://assets.sennheiser.com/global-downloads/file/12146/TI_1245_v1.8.0_Sennheiser_Sound_Control_Protocol_TCC2_EN.pdf)
            responses: how many responses are expected to arrive back
        """
        res = []
        if self.address is None or self.address == ('0.0.0.0', 45):
            print("WARNING: Microphone address not specified!")
            return res
        self.sock.sendto(bytes(command, 'ascii'), self.address)
        self.sock.settimeout(0.1)
        received = 0
        while received < responses:
            try:
                data, addr = self.sock.recvfrom(1024)
            except TimeoutError:
                return ['{"osc":{"error":[408,{"desc":"Microphone timed out"}]}}']
            if addr == self.address:
                # all the microphone's responses end in CRLF
                res.append(data.decode("ascii").split("\r\n")[0])
                received += 1

        return res
