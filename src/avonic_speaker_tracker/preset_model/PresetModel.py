import numpy as np
import math
from typing_extensions import override

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.preset_model.preset import PresetCollection
from avonic_speaker_tracker.preset_model.preset_control import find_most_similar_preset
from microphone_api.microphone_control_api import MicrophoneAPI

class PresetModel(TrackingModel):
    preset_locations: PresetCollection = None
    prev_dir: np.ndarray = None

    def __init__(self, filename=None):
        self.prev_dir = np.array([0, 0, 1])
        self.preset_locations = PresetCollection(filename=filename)
        self.preset_locations.load()

    @override
    def reload(self):
        self.preset_locations.load()

    @override
    def point(self, cam_api: CameraAPI, mic_api: MicrophoneAPI) -> np.array:
        """ Calculates the direction to which the camera should point so that
            it is the closest to an existing preset.
            Args:
                cam_api: The controller for the camera
                mic_api: The controller for the microphone
            Returns: the vector in which direction the camera should point and zoom value
        """
        print("Using presets")
        preset_names = np.array(self.preset_locations.get_preset_list())
        mic_direction = mic_api.get_direction()
        if isinstance(mic_direction, str):
            print(mic_direction)
            return self.prev_dir

        if len(self.preset_locations.get_preset_list()) == 0:
            print("No locations preset")
            return self.prev_dir

        presets_mic = []
        for i in range(len(preset_names)):
            presets_mic.append(self.preset_locations.get_preset_info(preset_names[i])[1])

        preset_id = find_most_similar_preset(mic_direction, presets_mic)
        preset = self.preset_locations.get_preset_info(preset_names[preset_id])
        direct = [int(np.rad2deg(preset[0][0])), int(np.rad2deg(preset[0][1])), preset[0][2]]

        diffX = math.fabs(self.prev_dir[0]-direct[0])*2
        diffY = math.fabs(self.prev_dir[1]-direct[1])*2

        speedX = diffX/360*24
        speedY = diffY/120*20

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
