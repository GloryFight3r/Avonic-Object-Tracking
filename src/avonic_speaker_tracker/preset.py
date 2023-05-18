import numpy as np


class Preset:
    def __init__(self, camera_angle: np.ndarray, microphone_direction: np.ndarray):
        self.camera_angle = camera_angle
        self.microphone_direction = microphone_direction


class PresetCollection:
    def __init__(self):
        self.preset_locations = dict()

    def add_preset(self, to_add: str, cam_angle: np.ndarray, microphone_direction: np.ndarray) -> None:
        """ Adds a preset to the dictionary of presets with the given name

        Args:
            to_add: Name of the preset
            cam_angle: Angle of the camera
            microphone_direction: Direction of the speaker
        """
        assert to_add not in self.preset_locations
        self.preset_locations[to_add] = Preset(cam_angle, microphone_direction)

    def remove_preset(self, to_remove: str):
        """ Removes a preset from the dictionary of presets with the given name

        Args:
            to_remove: Name of the preset 
        """
        assert to_remove in self.preset_locations
        del self.preset_locations[to_remove]

    def edit_preset(self, to_edit: str, new_cam_angle: np.ndarray, new_microphone_direction: np.ndarray):
        """ Edits a preset with the given name only if it is already inside the dictionary

        Args:
            to_edit: Name of the preset
            new_cam_angle: Angle of the camera
            new_microphone_direction: Direction of the speaker
        """
        assert to_edit in self.preset_locations
        self.preset_locations[to_edit] = Preset(new_cam_angle, new_microphone_direction)

    def get_preset_list(self):
        """ Returns a list with the names of the presets

        Returns: List with presets names
            
        """
        return list(self.preset_locations.keys())

    def get_preset_info(self, to_get: str):
        """ Returns the camera angle and microphone direction for a preset with a given name

        Args:
            to_get: Name of the preset

        Returns: Camera angle and microphone direction for the given preset
            
        """
        assert to_get in self.preset_locations
        return (self.preset_locations[to_get].camera_angle, 
                self.preset_locations[to_get].microphone_direction)    
