import numpy as np

class Calibration:
    # height of the microphone above the speaker
    mic_height: float = 1.0
    mic_to_cams: [np.array] = []
    mic_to_cam: np.array = None

    # variables of calibration
    speaker_points: [(np.array, np.array)] = []
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
        self.speaker_points.append(speaker_point)

    def add_direction_to_mic(self, to_mic: np.array):
        """ Add the direction from the camera to the microphone.

            params:
                to_mic: the direction as a 3D vector
        """
        self.to_mic_direction = to_mic

    def reset_calibration(self):
        """ Reset the calibration. To be used in case calibration went wrong or one of the devices moved. """
        self.mic_to_cams = []
        self.mic_to_cam = None
        self.speaker_points = []
        self.to_mic_direction = None

    def is_calibrated(self) -> bool:
        """ Check whether the system has been calibrated by checked whether the needed vectors are set.

            returns:
                is_calibrated: a boolean indicating whether the system is calibrated
        """
        return self.speaker_points != [] and self.to_mic_direction is not None

    def calculate_distance(self) -> np.array:
        """ Calculate the vectors from the microphone to the camera using the vectors acquired during calibration.
            This vector has a norm equal to the distance from the microphone to the camera. Since multiple points
            are used for the speaker, we get multiple similar vectors to the camera. The vector to use for further
            calculations is the average of these (self.mic_to_cam).

            returns:
                the 3D vector from the microphone to the camera
        """
        for speaker in self.speaker_points:
            cam_vecw = speaker[0]
            mic_vecw = speaker[1]
            assert mic_vecw[1] != 0.0 and self.mic_height != 0.0

            # calculate the length of the mic_vec
            mic_vec = mic_vecw / mic_vecw[1] * -self.mic_height

            # calculate the two angles needed
            alpha_cos = angle_between_vectors(cam_vecw, mic_vecw)
            beta_cos = angle_between_vectors(cam_vecw, self.to_mic_direction)
            alpha_sin = (1- alpha_cos**2)**0.5
            beta_sin = (1- beta_cos**2)**0.5
            assert beta_sin != 0.0

            mic_to_cam_dist = np.linalg.norm(mic_vec) / beta_sin * alpha_sin
            mic_to_cam = self.to_mic_direction / np.linalg.norm(self.to_mic_direction) * -mic_to_cam_dist
            self.mic_to_cams.append(mic_to_cam)

        self.mic_to_cam = np.mean(self.mic_to_cams, axis=0)
        print(self.mic_to_cam)
        return self.mic_to_cam

    def angle_between_vectors(p: np.array, q: np.array) -> float:
        return p.dot(q) / (np.linalg.norm(p) * np.linalg.norm(q))
