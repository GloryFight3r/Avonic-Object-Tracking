import time
import numpy as np

from maat_camera_api.camera_control_api import CameraAPI
from maat_tracking.utils.TrackingModel import TrackingModel
from maat_tracking.preset_model.preset import PresetCollection
from maat_tracking.preset_model.preset_control import find_most_similar_preset
from maat_microphone_api.microphone_control_api import MicrophoneAPI


class PresetModel(TrackingModel):
    """ Class that finds the location of the speaker in a set of
    recorded preset locations or the closest one in that set
    and points the camera towards that location.
    """
    def __init__(self, cam_api: CameraAPI, mic_api: MicrophoneAPI, filename: str = ""):
        """ Default constructor
            Args:
                cam_api: Controller for the camera
                mic_api: Controller for the microphone
                filename: location of the file that contains the preset information
        """
        self.prev_dir: np.ndarray = np.array([0, 0, 1])
        self.preset_locations: PresetCollection = PresetCollection(filename=filename)
        self.cam_api = cam_api
        self.mic_api = mic_api

    def point(self) -> np.ndarray:
        """ Calculates the direction to which the camera should point so that
            it is the closest to an existing preset.
            In addition to calculating the direction, performs movement of the camera.

            Returns: the vector in which direction the camera should point and zoom value
        """
        print("Using presets point method")
        preset_names: np.ndarray = np.array(self.preset_locations.get_preset_list())
        mic_direction = self.mic_api.get_direction()
        if isinstance(mic_direction, str):
            print(mic_direction)
            return self.prev_dir

        if len(self.preset_locations.get_preset_list()) == 0:
            print("No locations preset")
            return self.prev_dir

        presets_mic = []
        for i in range(len(preset_names)):
            presets_mic.append(self.preset_locations.get_preset_info(preset_names[i])[1])

        # Find the closest preset and the direction of the camera towards that
        preset = self.preset_locations.get_preset_info(
            preset_names[find_most_similar_preset(mic_direction, presets_mic)])
        direct = np.array([int(np.rad2deg(preset[0][0])) % 360,
                           int(np.rad2deg(preset[0][1])) % 360, preset[0][2]])

        # If either pitch and yaw is more than 180 degrees
        # camera should rotate in the opposite direction
        if direct[0] > 180:
            direct[0] = direct[0]-360
        if direct[1] > 180:
            direct[1] = direct[1]-360

        # If the direction to move is the same as the current direction camera will not move
        if direct is None:
            print("Something went wrong with direct here")
            return self.prev_dir

        if self.prev_dir[0] != direct[0] or self.prev_dir[1] != direct[1]:
            self.cam_api.move_absolute(24, 20, direct[0], direct[1])

        if self.prev_dir[2] != direct[2]:
            self.cam_api.direct_zoom(direct[2])
        self.prev_dir = direct

        return direct

    def set_filename(self, filename: str):
        self.preset_locations.set_filename(filename)

    def sleep(self):
        time.sleep(0.05)
