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

    def set_height(self, height: float):
        """ Sets the height of the microphone above the speaker.

            params:
                height: the new height
        """
        self.mic_height = height

    def add_speaker_point(self, speaker_point: (np.array, np.array)):
        """ Add the point at which the calibrator is speaking.

            params:
                speaker_point: the camera direction and the microphone direction respectively
        """
        self.speaker_point = speaker_point

    def add_direction_to_mic(self, to_mic: np.array):
        """ Add the direction from the camera to the microphone.

            params:
                to_mic: the direction as a 3D vector
        """
        self.to_mic_direction = to_mic

    def reset_calibration(self):
        """ Reset the calibration. To be used in case calibration went wrong or one of the devices moved. """
        self.mic_to_cam = None
        self.speaker_point = None
        self.to_mic_direction = None

    def is_calibrated(self) -> bool:
        """ Check whether the system has been calibrated by checked whether the needed vectors are set.

            returns:
                is_calibrated: a boolean indicating whether the system is calibrated
        """
        return not (self.speaker_point is None or self.to_mic_direction is None)

    def calculate_distance(self) -> np.array:
        """ Calculate the vector from the microphone to the camera using the vectors acquired during calibration.
            This vector has a norm equal to the distance from the microphone to the camera.

            returns:
                the 3D vector from the microphone to the camera
        """
        cam_vecw = self.speaker_point[0]
        mic_vecw = self.speaker_point[1]
        assert mic_vecw[1] != 0.0 and self.mic_height != 0.0

        # calculate the length of the mic_vec
        mic_vec = mic_vecw / mic_vecw[1] * -self.mic_height

        # calculate the two angles needed
        alpha = angle_between_vectors(cam_vecw, mic_vecw)
        beta = angle_between_vectors(cam_vecw, self.to_mic_direction)
        assert beta != 0.0

        mic_to_cam_dist = np.linalg.norm(mic_vec) / np.sin(beta) * np.sin(alpha)
        self.mic_to_cam = self.to_mic_direction / np.linalg.norm(self.to_mic_direction) * -mic_to_cam_dist
        return self.mic_to_cam
