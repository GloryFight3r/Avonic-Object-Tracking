import math
import time
import numpy as np
from maat_camera_api.camera_control_api import CameraAPI
from maat_camera_api.converter import vector_angle
from maat_tracking.utils.TrackingModel import TrackingModel
from maat_tracking.utils.coordinate_translation\
    import translate_microphone_to_camera_vector
from maat_tracking.audio_model.calibration import Calibration
from maat_microphone_api.microphone_control_api import MicrophoneAPI


class AudioModelNoAdaptiveZoom(TrackingModel):
    """ Class for tracking a speaker using the audio information from the microphone.
    Given that information it calculates the direction to which to point the camera
    having an existing calibration information and subsequently points it there. 
    This class does NOT implement adaptive zooming for the camera 
    depending on the distance of the speaker to it.
    This class still has the implementation of adaptive rotation speed depending 
    on how much the camera has to move.
    """
    def __init__(self, cam_api: CameraAPI, mic_api: MicrophoneAPI, filename: str = ""):
        """ Constructor for the AudioModelNoAdaptiveZoom

            Args:
                cam_api: Controller for the camera
                mic_api: Controller for the microphone
                filename: location of the file that contains the calibration information
        """
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.prev_dir: np.ndarray = np.array([0, 0, 1])
        self.calibration: Calibration = Calibration(filename=filename)
        self.calibration.load()

    def point(self) -> np.ndarray:
        """ Calculates the direction of the camera, so it point to the speaker.
            Based on so-called audio model that relies ONLY on microphone
            information for pointing.
            In addition to calculating the direction, performs movement of the camera.
            Returns: the vector in which direction the camera should point and zoom value.
        """
        if not self.mic_api.is_speaking():
            return self.prev_dir
        mic_direction = self.mic_api.get_direction()
        print("Current calibration mic -> cam vector: ", self.calibration.mic_to_cam)

        if isinstance(mic_direction, str):
            print(mic_direction)
            return self.prev_dir

        try:
            cam_vec = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                            mic_direction,
                                                            self.calibration.mic_height)
        except AssertionError:
            return self.prev_dir

        direct = vector_angle(cam_vec)

        direct_np = np.array([int(np.rad2deg(direct[0])) % 360,
                              int(np.rad2deg(direct[1])) % 360, self.prev_dir[2]])

        # If either pitch or yaw is more than 180 degrees
        # the camera should rotate in the opposite direction
        if direct_np[0] > 180:
            direct_np[0] = direct_np[0]-360
        if direct_np[1] > 180:
            direct_np[1] = direct_np[1]-360

        # Calculates the relative rotation of the camera
        diff_x = math.fabs(self.prev_dir[0]-direct_np[0])*2.0/360.0
        diff_y = math.fabs(self.prev_dir[1]-direct_np[1])*2.0/120.0

        # Sets the rotation speed depending on the amount of rotation
        speed_x: int = int(13 + diff_x*11.0)
        speed_y: int = int(11 + diff_y*9.0)

        speed_x = min(speed_x, 24)
        speed_y = min(speed_y, 20)

        # If the direction to move is the same as the current direction camera will not move
        if direct is None:
            return self.prev_dir

        if self.prev_dir[0] != direct_np[0] or self.prev_dir[1] != direct_np[1]:
            try:
                self.cam_api.move_absolute(speed_x, speed_y, direct_np[0], direct_np[1])
            except AssertionError:
                pass
            except Exception as e:
                print("Unexpected error while trying to move camera: ", e)

        if self.prev_dir[2] != direct_np[2]:
            self.cam_api.direct_zoom(direct_np[2])

        self.prev_dir = direct_np
        return direct_np

    def set_filename(self, filename: str):
        """ Setter for the location of the file containing the calibration info
        """
        self.calibration.set_filename(filename)

    def sleep(self):
        time.sleep(0.2)
