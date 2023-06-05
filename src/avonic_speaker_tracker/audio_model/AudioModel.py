import numpy as np
import math
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.converter import vector_angle
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.utils.coordinate_translation\
    import translate_microphone_to_camera_vector
from avonic_speaker_tracker.audio_model.calibration import Calibration
from microphone_api.microphone_control_api import MicrophoneAPI

class AudioModel(TrackingModel):
    calibration: Calibration = None
    prev_dir: np.ndarray = None
    speak_delay: int = 0

    def __init__(self, filename=None):
        self.prev_dir = np.array([0, 0, 1])
        self.calibration = Calibration(filename=filename)
        self.calibration.load()

    def set_speak_delay(self, speak_delay = 0):
        self.speak_delay = speak_delay

    def point(self, cam_api: CameraAPI, mic_api: MicrophoneAPI) -> np.ndarray:
        """ Calculates the direction of the camera, so it point to the speaker.
            Based on so-called audio model that relies ONLY on microphone
            information for pointing.
            In addition to calculating the direction, performs movement of the camera.
            Args:
                cam_api: The controller for the camera
                mic_api: The controller for the microphone
            Returns: the vector in which direction the camera should point and zoom value.
        """
        if self.speak_delay == 100:
            cam_api.direct_zoom(0)
            self.prev_dir[2]=0
            return self.prev_dir
        mic_direction = mic_api.get_direction()
        print("LOL", self.calibration.mic_to_cam)

        if isinstance(mic_direction, str):
            print(mic_direction)
            return self.prev_dir

        cam_vec = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                        mic_direction,
                                                        self.calibration.mic_height)

        vec_len = np.sqrt(cam_vec.dot(cam_vec))
        vec_len = min(vec_len,10.0)
        zoom_val = (int)((vec_len/10.0)*16000)


        direct = vector_angle(cam_vec)

        direct = [int(np.rad2deg(direct[0])), int(np.rad2deg(direct[1])), zoom_val]

        diffX = math.fabs(self.prev_dir[0]-direct[0])*2
        diffY = math.fabs(self.prev_dir[1]-direct[1])*2

        speedX = (int)(13 + diffX/360*11)
        speedY = (int)(11 + diffY/120*9)

        speedX = min(speedX,24)
        speedY = min(speedY,20)

        if direct is None:
            return self.prev_dir

        if self.prev_dir[0] != direct[0] or self.prev_dir[1] != direct[1]:
            cam_api.move_absolute(speedX, speedY, direct[0], direct[1])

        if self.prev_dir[2] != direct[2]:
            cam_api.direct_zoom(direct[2])

        self.prev_dir = direct
        return direct
