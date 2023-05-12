import numpy as np
from avonic_camera_api.converter import angle_vector
from avonic_speaker_tracker.math_helper import angle_between_vectors

class Calibration:
    # height of the microphone above the speaker
    mic_height: float = 1.0
    mic_to_cam: np.array = None

    # variables of calibration
    speaker_point: (np.array, np.array) = None
    to_mic_direction: np.array = None
    to_cam_direction: np.array = None

    def set_height(self, height: float):
        self.mic_height = height

    def add_speaker_point(self, speaker_point: (np.array, np.array)):
        self.speaker_point = speaker_point

    def add_direction_to_mic(self, to_mic: np.array):
        self.to_mic_direction = to_mic

    def add_direction_to_cam(self, to_cam: np.array):
        self.to_cam_direction = to_cam

    def reset_calibration(self):
        self.mic_to_cam = None
        self.speaker_point = None
        self.to_mic_direction = None
        self.to_cam_direction = None

    def is_calibrated(self) -> bool:
        return not (self.speaker_point is None or self.to_mic_direction is None \
            or self.to_cam_direction is None)

    def calculate_distance(self) -> np.array:
        cam_vecw = angle_vector(self.speaker_point[0][0], self.speaker_point[0][1])
        mic_vecw = self.speaker_point[1]
        assert mic_vecw[1] != 0.0 and self.mic_height != 0.0

        # calculate the length of the mic_vec
        mic_vec = mic_vecw / mic_vecw[1] * -self.mic_height

        # calculate the two angles needed
        alpha = angle_between_vectors(cam_vecw, mic_vecw)
        beta = angle_between_vectors(cam_vecw, angle_vector(self.to_mic_direction[0], self.to_mic_direction[1]))
        assert beta != 0.0

        mic_to_cam_dist = np.linalg.norm(mic_vec) / np.sin(beta) * np.sin(alpha)
        self.mic_to_cam = self.to_cam_direction / np.linalg.norm(self.to_cam_direction) * mic_to_cam_dist
        return self.mic_to_cam
