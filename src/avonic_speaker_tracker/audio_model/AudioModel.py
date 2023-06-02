import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.converter import vector_angle
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.utils.coordinate_translation\
    import translate_microphone_to_camera_vector
from avonic_speaker_tracker.audio_model.calibration import Calibration
from microphone_api.microphone_control_api import MicrophoneAPI

class AudioModel(TrackingModel):
    calibration: Calibration = None
    prev_dir: np.array = None

    def __init__(self, filename=None):
        self.prev_dir = np.array([0, 0, 1])
        self.calibration = Calibration(filename=filename)
        self.calibration.load()
        print("CALIBRATION !!!!", self.calibration.mic_to_cam)

    def point(self, cam_api: CameraAPI, mic_api: MicrophoneAPI):
        print("CALIBRATION !!!!", self.calibration.mic_to_cam)
        """ Calculates the direction of the camera, so it point to the speaker.
            Based on so-called audio model that relies ONLY on microphone
            information for pointing.
            Args:
                cam_api: The controller for the camera
                mic_api: The controller for the microphone
            Returns: the vector in which direction the camera should point and zoom value.
        """
        mic_direction = mic_api.get_direction()
        if isinstance(mic_direction, str):
            print(mic_direction)
            return None

        cam_vec = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                        mic_direction,
                                                        self.calibration.mic_height)

        direct = vector_angle(cam_vec)
        direct = [int(np.rad2deg(direct[0])), int(np.rad2deg(direct[1])), 0]
        return direct


