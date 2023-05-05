import json
from microphone_api.microphone_adapter import UDPSocket


class MicrophoneAPI:
    sock = None
    elevation = None
    azimuth = None
    speaking = None

    def __init__(self, sock: UDPSocket):
        self.sock = sock
        self.elevation = 0
        self.azimuth = 0
        self.speaking = False

    def get_azimuth(self) -> int:
        message = '{"m":{"beam":{"azimuth":null}}}'
        ret = self.sock.send(message)[0]
        res = json.loads(ret)["m"]["beam"]["azimuth"] | 0
        assert isinstance(res, int)
        return res

    def get_elevation(self) -> int:
        message = '{"m":{"beam":{"elevation":null}}}'
        ret = self.sock.send(message)[0]
        res = json.loads(ret)["m"]["beam"]["elevation"] | 0
        assert isinstance(res, int)
        return res

    def get_direction(self) -> (int, int):
        message = '{"m":{"beam":{"azimuth":null,"elevation":null}}}'
        ret = self.sock.send(message)[0]
        json_object = json.loads(ret)["m"]["beam"]
        azimuth = json_object["azimuth"] | 0
        elevation = json_object["elevation"] | 0
        assert isinstance(azimuth, int)
        assert isinstance(elevation, int)
        return self.get_vector()

    def get_vector(self):
        # TODO: STUB
        return [0.0, 0.0, 1.0]

    def is_speaking(self):
        # TODO: STUB
        return self.speaking
