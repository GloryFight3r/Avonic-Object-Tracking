import math

import numpy as np

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.converter import vector_angle
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.utils.coordinate_translation\
    import translate_microphone_to_camera_vector
from avonic_speaker_tracker.audio_model.calibration import Calibration
from microphone_api.microphone_control_api import MicrophoneAPI

class AudioModel(TrackingModel):
    """ Class for tracking a speaker using the audio information from the microphone.
    Given that information it calculates the direction to which to point the camera
    having an existing calibration information and subsequently points it there. 
    This class implements adaptive zooming for the camera 
    depending on the distance of the speaker to it.
    """
    def __init__(self, cam_api: CameraAPI, mic_api: MicrophoneAPI, filename: str = ""):
        """ Constructor for the AudioModel 

            Args:
                cam_api: Controller for the camera
                mic_api: Controller for the microphone
                filename: location of the file that contains the calibration information
        """
        self.prev_dir: np.ndarray = np.array([0, 0, 1])
        self.cam_api = cam_api
        self.speak_delay: int = 0
        self.mic_api = mic_api
        self.calibration: Calibration = Calibration(filename=filename)
        self.calibration.load()
    
    def set_speak_delay(self, speak_delay: int = 0):
        """ Sets the time elapsed since the last person spoke

            Args:
                speak_delay: integer in range[0:100] 
        """
        self.speak_delay = speak_delay

    def point(self):
        """ Calculates the direction of the camera, so it point to the speaker.
            Based on so-called audio model that relies ONLY on microphone
            information for pointing.

            Returns: the vector in which direction the camera should point and zoom value.
        """
        # reset speak delay some is speaking, else count up till 100 at which point we zoom out
        if self.mic_api.is_speaking():
            self.speak_delay = 0
        elif self.speak_delay < 100:
            self.speak_delay += 1
        elif self.speak_delay == 100:
            self.cam_api.direct_zoom(0)
            self.prev_dir[2] = 0
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

        # Calculates the distance from the camera to the speaker
        vec_len = np.sqrt(cam_vec.dot(cam_vec))
        vec_len = min(vec_len,10.0)

        # Sets the zoom value to an appropriate value depending the the distance
        zoom_val = (int)((vec_len/10.0)*16000)

        direct = vector_angle(cam_vec)
        direct_np = np.array([int(np.rad2deg(direct[0]))%360, int(np.rad2deg(direct[1]))%360, zoom_val])

        # If either pitch an yaw is more than 180 degrees camera should rotate in the opposite direction
        if direct_np[0]>180:
            direct_np[0] = direct_np[0]-360
        if direct_np[1]>180:
            direct_np[1] = direct_np[1]-360

        # Calculates the relative rotation of the camera
        diffX = math.fabs(self.prev_dir[0]-direct_np[0])*2.0/360.0
        diffY = math.fabs(self.prev_dir[1]-direct_np[1])*2.0/120.0

        # Sets the rotation speed depending on the amount of rotation
        speedX : int = int(13 + diffX*11.0)
        speedY : int = int(11 + diffY*9.0)

        speedX = min(speedX,24)
        speedY = min(speedY,20)

        # If the direction to move is the same as the current direction camera will not move
        if direct is None:
            return self.prev_dir

        if self.prev_dir[0] != direct_np[0] or self.prev_dir[1] != direct_np[1]:
            self.cam_api.move_absolute(speedX, speedY, direct_np[0], direct_np[1])

        if self.prev_dir[2] != direct_np[2]:
            self.cam_api.direct_zoom(direct_np[2])

        self.prev_dir = direct_np

        return direct_np

    def set_filename(self, filename: str):
        """ Setter for the location of the file containing the calibration info
        """
        self.calibration.set_filename(filename)
