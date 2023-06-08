import json
import numpy as np
from avonic_speaker_tracker.utils.persistency_utils import CustomEncoder

class Calibration:
    def __init__(self, filename: str = ""):
        self.filename = filename

        # height of the microphone above the speaker
        self.mic_height: float = 1.0
        self.mic_to_cams: list[np.ndarray] = []
        self.mic_to_cam: np.ndarray = np.array([0.0, 0.0, 0.0])

        # variables of calibration
        self.speaker_points: list[tuple[np.ndarray, np.ndarray]] = []
        self.to_mic_direction: np.ndarray = np.array([0.0, 0.0, 0.0])

        self.load()

    def set_height(self, height: float):
        """ Sets the height of the microphone above the speaker.

            params:
                height: the new height
        """
        self.mic_height = height
        self.record()

    def add_speaker_point(self, speaker_point: tuple[np.ndarray, np.ndarray]):
        """ Add the point at which the calibrator is speaking.

            params:
                speaker_point: the camera direction and the microphone direction respectively
        """
        self.speaker_points.append(speaker_point)
        self.record()

    def add_direction_to_mic(self, to_mic: np.ndarray):
        """ Add the direction from the camera to the microphone.

            params:
                to_mic: the direction as a 3D vector
        """
        self.to_mic_direction = to_mic
        self.record()

    def reset_calibration(self):
        """ Reset the calibration. To be used in case calibration
        went wrong or one of the devices moved. """
        self.mic_to_cams = []
        self.mic_to_cam = np.array([0.0, 0.0, 0.0])
        self.speaker_points = []
        self.to_mic_direction = np.array([0.0, 0.0, 0.0])
        self.record()

    def is_calibrated(self) -> bool:
        """ Check whether the system has been calibrated by
        checked whether the needed vectors are set.

            returns:
                is_calibrated: a boolean indicating whether the system is calibrated
        """
        return bool(self.speaker_points) \
            and self.to_mic_direction is not None \
            and not np.allclose(self.to_mic_direction, np.array([0.0, 0.0, 0.0]))

    def calculate_distance(self) -> np.ndarray:
        """ Calculate the vectors from the microphone to the camera
            using the vectors acquired during calibration.
            This vector has a norm equal to the distance from the
            microphone to the camera. Since multiple points
            are used for the speaker, we get multiple similar vectors to the camera.
            The vector to use for further calculations is the average of these (self.mic_to_cam).

            returns:
                the 3D vector from the microphone to the camera
        """
        if len(self.speaker_points) == 0:
            return self.mic_to_cam

        # reset the list so no old calculations are used
        self.mic_to_cams = []
        for speaker in self.speaker_points:
            cam_vecw = speaker[0]
            mic_vecw = speaker[1]
            assert mic_vecw[1] != 0.0 and self.mic_height != 0.0

            # calculate the length of the mic_vec
            mic_vec = mic_vecw / mic_vecw[1] * self.mic_height

            # calculate the two angles needed
            alpha_cos = angle_between_vectors(cam_vecw, mic_vecw)
            beta_cos = angle_between_vectors(cam_vecw, self.to_mic_direction)
            alpha_sin = (1- alpha_cos**2)**0.5
            beta_sin = (1- beta_cos**2)**0.5
            assert abs(beta_sin) >= 1e-5

            mic_to_cam_dist = np.linalg.norm(mic_vec) / beta_sin * alpha_sin
            mic_to_cam = self.to_mic_direction \
                / np.linalg.norm(self.to_mic_direction) * -mic_to_cam_dist
            self.mic_to_cams.append(mic_to_cam)

        self.mic_to_cam = np.mean(self.mic_to_cams, axis=0)
        return self.mic_to_cam

    def record(self):
        if self.filename != "":
            with open(self.filename, "w", encoding="utf-8") as outfile:
                outfile.write(json.dumps({
                    "speaker_points" :self.speaker_points,
                    "to_mic_direction": self.to_mic_direction,
                    "mic_height": self.mic_height
                    }, indent=4, cls=CustomEncoder))

    def load(self):
        if self.filename != "":
            try:
                with open(self.filename, encoding="utf-8") as f:
                    print(f"Loading calibration json from {self.filename}...")
            except FileNotFoundError:
                with open(self.filename, "x", encoding="utf-8") as outfile:
                    print(f"No file {self.filename} was found. Create new preset json...")
                    outfile.write(json.dumps({"speaker_points": [],
                    "to_mic_direction": [0.0, 0.0, 0.0], "mic_height": 1.0}, indent=4))
            try:
                with open(self.filename, encoding="utf-8") as f:
                    data = json.load(f)
                    self.speaker_points = []
                    for key in data["speaker_points"]:
                        self.speaker_points.append((np.array(key[0]),
                            np.array(key[1])))
                        assert len(key[0]) == 3
                        assert len(key[1]) == 3
                    self.to_mic_direction = np.array(data["to_mic_direction"])
                    assert len(data["to_mic_direction"]) == 3
                    self.mic_height = float(data["mic_height"])
                    self.calculate_distance()
                    print("Loaded speaker points: ", self.speaker_points)
                    print("Loaded camera to microphone vector: ", self.to_mic_direction)
                    print("Loaded microphone height: ", self.mic_height)
            except:
                print("The appplication couldn't load calibration data from specified files. "
                    + "Please check your config files. Exiting...")
                raise SystemExit


def angle_between_vectors(p: np.ndarray, q: np.ndarray) -> float:
    """ Calculates the cosine of the smallest angle between two vectors.

        params:
            p: the first vector
            q: the second vector

        returns:
            angle: the cosine of the angle
    """
    return p.dot(q) / (np.linalg.norm(p) * np.linalg.norm(q))
