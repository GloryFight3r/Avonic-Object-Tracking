import json
import numpy as np
from microphone_api.microphone_adapter import UDPSocket


class MicrophoneAPI:
    sock = None
    elevation = None
    azimuth = None
    speaking = None
    threshold = None

    def __init__(self, sock: UDPSocket, threshold=-55):
        """ Constructor for the Microphone

        Args:
            sock: wrapper for the socket
        """
        self.sock = sock
        self.elevation = 0.0
        self.azimuth = 0.0
        self.speaking = False
        self.threshold = threshold

    def get_azimuth(self) -> float:
        """ Get azimuth from the camera.

        Returns:
            the azimuth in radians
        """
        message = '{"m":{"beam":{"azimuth":null}}}'
        ret = self.sock.send(message)[0]
        res = json.loads(ret)["m"]["beam"]["azimuth"]
        assert isinstance(res, int)
        if 0 <= res <= 360:
            self.azimuth = np.deg2rad(res)
        return self.azimuth

    def get_elevation(self) -> float:
        """ Get elevation from the camera.

        Returns:
            the elevation in radians
        """
        message = '{"m":{"beam":{"elevation":null}}}'
        ret = self.sock.send(message)[0]
        res = json.loads(ret)["m"]["beam"]["elevation"]
        assert isinstance(res, int)
        if 0 <= res <= 90:
            self.elevation = np.deg2rad(res)
        return self.elevation

    def get_direction(self) -> np.array:
        """ Get direction vector from the camera.

        Returns:
            the direction vector (normalised)
        """
        message = '{"m":{"beam":{"azimuth":null,"elevation":null}}}'
        ret = self.sock.send(message)[0]
        json_object = json.loads(ret)["m"]["beam"]
        azimuth = json_object["azimuth"]
        elevation = json_object["elevation"]
        assert isinstance(azimuth, int)
        assert isinstance(elevation, int)
        if 0 <= elevation <= 90:
            self.elevation = np.deg2rad(elevation)
        if 0 <= azimuth < 360:
            self.azimuth = np.deg2rad(azimuth)
        return self.vector()

    def vector(self):
        """ Get direction vector from local variables

        Returns:
            the vector, pointing in [0, 0, 1] when elevation and azimuth 0
            (aka. Sennheiser logo should point away from camera by default)
        """
        cose = np.cos(self.elevation)
        return np.array([np.sin(self.azimuth) * cose, -np.sin(self.elevation), np.cos(self.azimuth) * cose])

    def is_speaking(self):
        """ Determine whether someone is speaking based on the peak loudness

        Returns:
            whether the peak loudness is higher than the threshold
        """
        message = '{"m":{"in1":{"peak":null}}}'
        ret = self.sock.send(message)[0]
        res = json.loads(ret)["m"]["in1"]["peak"]
        assert isinstance(res, int)
        if -90 <= res <= 0:
            self.speaking = res > self.threshold
        return self.speaking
