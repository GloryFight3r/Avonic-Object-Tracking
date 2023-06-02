from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.utils.coordinate_translation import translate_microphone_to_camera_vector
from avonic_speaker_tracker.audio_model.calibration import Calibration
from avonic_camera_api.converter import vector_angle

class AudioModel(TrackingModel):
    calibration: Calibration = None
    prev_dir: np.array = None
    
    def __init__(self, filename=None):
        self.prev_dir = np.array([0, 0, 0])
        self.calibration = Calibration(filename=filename)
    
    def point(self, cam_api: CameraAPI, mic_api: MicrophoneAPI):
        """ Points the camera towards the calculated direction from either:
        the presets or the continuous follower.
            Args:
                cam_api: The controller for the camera
                mic_api: The controller for the microphone
                preset_locations: Collection containing all current presets
                preset_use: True if we are using presets and false otherwise
                calibration: Information on the calibration of the system
                prev_dir: The previous direction to which the camera was pointing
            Returns: the pitch and yaw of the camera and the zoom value
        """
        """ Calculates the direction of the camera, so it point to the speaker.
            Args:
                mic_api: The controller for the microphone
                calibration: Information on the calibration of the system
            Returns: the pitch and yaw of the camera and the zoom value
        """
        mic_direction = mic_api.latest_direction

        cam_vec = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                        mic_direction,
                                                        self.calibration.mic_height)

        direct = vector_angle(cam_vec)
        direct = [int(np.rad2deg(direct[0])), int(np.rad2deg(direct[1])), 0]

        if self.prev_dir[0] != direct[0] or self.prev_dir[1] != direct[1]:
            cam_api.move_absolute(24, 20, direct[0], direct[1])
            cam_api.direct_zoom(direct[2])
            self.prev_dir = direct
        return direct
