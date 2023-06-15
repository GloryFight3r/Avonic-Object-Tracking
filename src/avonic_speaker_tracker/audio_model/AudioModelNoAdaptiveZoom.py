import math
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.converter import vector_angle
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.utils.coordinate_translation\
    import translate_microphone_to_camera_vector
from avonic_speaker_tracker.audio_model.calibration import Calibration
from microphone_api.microphone_control_api import MicrophoneAPI

class AudioModelNoAdaptiveZoom(TrackingModel):
    def __init__(self, filename: str = ""):
        self.prev_dir: np.ndarray = np.array([0, 0, 1])
        self.calibration: Calibration = Calibration(filename=filename)
        self.calibration.load()

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
        mic_direction = mic_api.get_direction()
        print("Current calibration mic -> cam vector: ", self.calibration.mic_to_cam)

        if isinstance(mic_direction, str):
            print(mic_direction)
            return self.prev_dir

        cam_vec = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                        mic_direction,
                                                        self.calibration.mic_height)

        vec_len = np.sqrt(cam_vec.dot(cam_vec))
        vec_len = min(vec_len,10.0)


        direct = vector_angle(cam_vec)

        direct_np = np.array([int(np.rad2deg(direct[0]))%360, 
                int(np.rad2deg(direct[1]))%360, self.prev_dir[2]])

        if direct_np[0]>180:
            direct_np[0] = direct_np[0]-360
        if direct_np[1]>180:
            direct_np[1] = direct_np[1]-360

        diffX = math.fabs(self.prev_dir[0]-direct_np[0])*2.0/360.0
        diffY = math.fabs(self.prev_dir[1]-direct_np[1])*2.0/120.0

        speedX : int = int(13 + diffX*11.0)
        speedY : int = int(11 + diffY*9.0)

        speedX = min(speedX,24)
        speedY = min(speedY,20)

        if direct is None:
            return self.prev_dir

        if self.prev_dir[0] != direct_np[0] or self.prev_dir[1] != direct_np[1]:
            cam_api.move_absolute(speedX, speedY, direct_np[0], direct_np[1])

        if self.prev_dir[2] != direct_np[2]:
            cam_api.direct_zoom(direct_np[2])

        self.prev_dir = direct_np
        return direct_np

    def set_filename(self, filename: str):
        self.calibration.set_filename(filename)
