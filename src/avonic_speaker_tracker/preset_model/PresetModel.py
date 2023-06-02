from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
import numpy as np
from avonic_speaker_tracker.preset_model.preset import PresetCollection
from avonic_speaker_tracker.preset_model.preset_control import find_most_similar_preset
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI

class PresetModel(TrackingModel):
    preset_locations: PresetCollection = None
    prev_dir: np.array = None
    def __init__(self, filename=None):
        self.prev_dir = np.array([0, 0, 0])
        self.preset_locations = PresetCollection(filename=filename)

    def point(self, cam_api: CameraAPI, mic_api: MicrophoneAPI) -> np.array:
        """ Calculates the direction to which the camera should point so that
            it is the closest to an existing preset.
            Args:
                cam_api: The controller for the camera
                mic_api: The controller for the microphone
            Returns: the vector in which direction the camera should point
        """
        preset_names = np.array(self.preset_locations.get_preset_list())
        mic_direction = mic_api.latest_direction

        if len(self.preset_locations.get_preset_list()) == 0:
            print("No locations preset")
            return self.prev_dir

        presets_mic = []
        for i in range(len(preset_names)):
            presets_mic.append(self.preset_locations.get_preset_info(preset_names[i])[1])

        preset_id = find_most_similar_preset(mic_direction, presets_mic)
        preset = self.preset_locations.get_preset_info(preset_names[preset_id])
        direct = [int(np.rad2deg(preset[0][0])), int(np.rad2deg(preset[0][1])), preset[0][2]]

        if self.prev_dir[0] != direct[0] or self.prev_dir[1] != direct[1]:
            cam_api.move_absolute(24, 20, direct[0], direct[1])
            cam_api.direct_zoom(direct[2])
            self.prev_dir = direct

        return direct
