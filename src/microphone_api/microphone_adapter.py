import socket


class UDPSocket:
    """
    This class contains methods to send and receive raw UDP packets to the microphone.
    """
    sock = None
    address = None

    def __init__(self, address,
                 sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)):
        """ Constructor for Microphone

        :param address: the ip and port in the format (ip, port)
        :param sock: a UDP socket
        """

        self.address = address
        self.sock = sock
        #self.sock.bind(self.address)

    def __del__(self):
        """ Destructor for Microphone
            Closes UDP connection
        """
        self.sock.close()

    def send(self, command: str, responses: int = 1) -> [str]:
        """ Send a command and wait for a response

        :param command: the command in JSON format (refer to
        https://assets.sennheiser.com/global-downloads/file/12146/TI_1245_v1.8.0_Sennheiser_Sound_Control_Protocol_TCC2_EN.pdf
        )
        :param responses: how many responses are expected to arrive back
        """
        res = []
        self.sock.sendto(bytes(command, 'ascii'), self.address)
        received = 0
        while received < responses:
            data, addr = self.sock.recvfrom(1024)
            if addr == self.address:
                # all the microphone's responses end in CRLF
                res.append(data.decode("ascii").split("\r\n")[0])
                received += 1

        return res
