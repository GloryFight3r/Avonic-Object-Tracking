import json
import numpy as np
from microphone_api.microphone_adapter import UDPSocket


class MicrophoneAPI:
    sock = None
    height = None
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
        self.height = 0.0
        self.elevation = 0.0
        self.azimuth = 0.0
        self.speaking = False
        self.threshold = threshold

    def set_height(self, height: float):
        """
        Sets the height of the microphone.

            Parameters:
                height (float): the new height
        """
        assert height >= 0.0
        self.height = height

    def get_azimuth(self) -> float:
        """ Get azimuth from the camera.

        Returns:
            the azimuth in radians
        """
        message = '{"m":{"beam":{"azimuth":null}}}'
        ret = self.sock.send(message)[0]
        try:
            res = json.loads(ret)["m"]["beam"]["azimuth"]
            assert isinstance(res, int)
            if 0 <= res <= 360:
                self.azimuth = np.deg2rad(res)
        except KeyError:
            print("Unable to get azimuth from the microphone, response was: " + ret)
        return self.azimuth

    def get_elevation(self) -> float:
        """ Get elevation from the camera.

        Returns:
            the elevation in radians
        """
        message = '{"m":{"beam":{"elevation":null}}}'
        ret = self.sock.send(message)[0]
        try:
            res = json.loads(ret)["m"]["beam"]["elevation"]
            assert isinstance(res, int)
            if 0 <= res <= 90:
                self.elevation = np.deg2rad(res)
        except KeyError:
            print("Unable to get elevation from microphone, response was: " + ret)
        return self.elevation

    def get_direction(self) -> np.array:
        """ Get direction vector from the microphone.

        Returns:
            the direction vector (normalised)
        """
        message = '{"m":{"beam":{"azimuth":null,"elevation":null}}}'
        ret = self.sock.send(message)[0]
        try:
            json_object = json.loads(ret)["m"]["beam"]
            azimuth = json_object["azimuth"]
            elevation = json_object["elevation"]
            assert isinstance(azimuth, int)
            assert isinstance(elevation, int)
            if 0 <= elevation <= 90:
                self.elevation = np.deg2rad(elevation)
            if 0 <= azimuth < 360:
                self.azimuth = np.deg2rad(azimuth)
        except KeyError:
            print("Unable to get direction from microphone, response was: " + ret)

        return self.vector()

    def vector(self):
        """ Get direction vector from local variables

        Returns:
            the vector, pointing in [0, 0, 1] when elevation and azimuth 0
            (aka. Sennheiser logo should point away from camera by default)
        """
        cose = np.cos(self.elevation)
        return np.array([-np.sin(self.azimuth) * cose,
                         -np.sin(self.elevation), np.cos(self.azimuth) * cose])

    def is_speaking(self):
        """ Determine whether someone is speaking based on the peak loudness

        Returns:
            whether the peak loudness is higher than the threshold
        """
        message = '{"m":{"in1":{"peak":null}}}'
        ret = self.sock.send(message)[0]
        try:
            res = json.loads(ret)["m"]["in1"]["peak"]
            assert isinstance(res, int)
            if -90 <= res <= 0:
                self.speaking = res > self.threshold
        except KeyError:
            print("Unable to get peak loudness, response was: " + ret)
        return self.speaking
