import requests
from enum import Enum

class ResponseCodeHTTP(Enum):
    """
    This enum contains the 8 possible camera response codes.
    """
    OK = 0
    ERROR = 1
    NO_CONNECTION = 2
    NO_ADDRESS = 3

class CameraHTTP:
    address:tuple[str, int]

    def __init__(self, address:tuple[str, int]):
        self.address = address
        
        if address is None or address == ('0.0.0.0', 80):
            print("WARNING: Camera address not specified!")
            self.address = ('0.0.0.0', 80)
            return

    def send(self, command:str)->tuple[ResponseCodeHTTP, str | None]:
        if self.address is None or self.address == ('0.0.0.0', 80):
            print("WARNING: Camera address or port not specified!")
            return (ResponseCodeHTTP.NO_ADDRESS, None)
        
        try:
            response = requests.get("http://" + self.address[0] + ":" + str(self.address[1]) + "/ajaxcom?szCmd=" + command)

            if response.status_code == 200:
                return (ResponseCodeHTTP.OK, response.json())
            else:
                return (ResponseCodeHTTP.ERROR, None)
        except:
            return (ResponseCodeHTTP.NO_CONNECTION, None)

