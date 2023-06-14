import json
from json import JSONDecodeError
import numpy as np
from microphone_api.microphone_adapter import MicrophoneSocket


class MicrophoneAPI:
    def __init__(self, sock: MicrophoneSocket, threshold: int = -55):
        """ Constructor for the Microphone

        Args:
            sock: wrapper for the socket
        """
        self.sock: MicrophoneSocket = sock
        self.elevation: float = 0.0
        self.azimuth: float = 0.0
        self.speaking: bool = False
        self.threshold: int = threshold
        self.prev_dir = np.array([0.0, 0.0, 1.0])

    def set_address(self, address):
        """
        Sets the address to send requests to

        Args:
            address: (IP, port)
        """
        ret = self.sock.connect(address)
        if not ret:
            return '{"message":"No address specified"}', False
        return '{"message":"Address set successfully"}', True

    def get_azimuth(self) -> float:
        """ Get azimuth from the camera.

        Returns:
            the azimuth in radians
        """
        message = '{"m":{"beam":{"azimuth":null}}}'
        sent = self.sock.send(message)
        if len(sent) == 0:
            print("Microphone returned nothing.")
            return self.azimuth
        ret = sent[0]
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
        sent = self.sock.send(message)
        if len(sent) == 0:
            print("Microphone returned nothing.")
            return self.elevation
        ret = sent[0]
        try:
            res = json.loads(ret)["m"]["beam"]["elevation"]
            assert isinstance(res, int)
            if 0 <= res <= 90:
                self.elevation = np.deg2rad(res)
        except KeyError:
            print("Unable to get elevation from microphone, response was: " + ret)
        return self.elevation

    def get_direction(self) -> np.ndarray | str:
        """ Get direction vector from the microphone.

        Returns:
            the direction vector (normalized)
        """
        message = '{"m":{"beam":{"azimuth":null,"elevation":null}}}'
        sent = self.sock.send(message)
        if len(sent) == 0:
            return "Microphone returned nothing."
        ret = sent[0]
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
            obj = json.loads(ret)
            if "osc" in obj and "error" in obj["osc"]:
                return json.dumps(obj["osc"]["error"])
            try:  # in case of peak message being received instead
                peak = obj["m"]["in1"]["peak"]
                assert isinstance(peak, int)
                if -90 <= peak <= 0:
                    self.speaking = peak > self.threshold
            except KeyError:
                return "Unable to get direction from microphone, response was: " + ret
        except JSONDecodeError:
            return "Did not receive a valid JSON," \
                   " are you sure you are communicating with the microphone? Received: " + ret
        return self.vector()

    def vector(self) -> np.ndarray:
        """ Get direction vector from local variables

        Returns:
            the vector, pointing in [0, 0, 1] when elevation and azimuth 0
            (aka. Sennheiser logo should point away from camera by default)
        """
        speaking = self.is_speaking()
        if isinstance(speaking, bool) and speaking:
            cose = np.cos(self.elevation)
            self.prev_dir = np.array([-np.sin(self.azimuth) * cose,
                            -np.sin(self.elevation), np.cos(self.azimuth) * cose])
        return self.prev_dir

    def is_speaking(self) -> bool | str:
        """ Determine whether someone is speaking based on the peak loudness

        Returns:
            whether the peak loudness is higher than the threshold
        """
        message = '{"m":{"in1":{"peak":null}}}'
        sent = self.sock.send(message)
        if len(sent) == 0:
            return "Microphone returned nothing."
        ret = sent[0]
        try:
            res = json.loads(ret)["m"]["in1"]["peak"]
            assert isinstance(res, int)
            if -90 <= res <= 0:
                self.speaking = res > self.threshold
        except KeyError:
            obj = json.loads(ret)
            if "osc" in obj and "error" in obj["osc"]:
                return json.dumps(obj["osc"]["error"])
            try:  # in case of receiving direction message instead
                azimuth = obj["m"]["beam"]["azimuth"]
                elevation = obj["m"]["beam"]["elevation"]
                assert isinstance(azimuth, int)
                assert isinstance(elevation, int)
                if 0 <= elevation <= 90:
                    self.elevation = np.deg2rad(elevation)
                if 0 <= azimuth < 360:
                    self.azimuth = np.deg2rad(azimuth)
            except KeyError:
                return "Unable to get peak loudness, response was: " + ret
        except JSONDecodeError:
            return "Did not receive a valid JSON," \
                   " are you sure you are communicating with the microphone? Received: " + ret
        return self.speaking
