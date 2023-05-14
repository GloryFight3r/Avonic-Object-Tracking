import numpy as np

class Preset:
    def __init__(self, camera_angle:np.ndarray, microphone_direction:np.ndarray):
        self.camera_angle = camera_angle
        self.microphone_direction = microphone_direction

class PresetCollection:
    def __init__(self):
        self.preset_locations = dict()

    def add_preset(self, to_add, cam_angle, microphone_direction):
        assert to_add not in self.preset_locations
        self.preset_locations[to_add] = Preset(cam_angle, microphone_direction)
    def remove_preset(self, to_remove):
        assert to_remove in self.preset_locations
        del self.preset_locations[to_remove]
    def edit_preset(self, to_edit, new_cam_angle, new_microphone_direction):
        assert to_edit in self.preset_locations
        self.preset_locations[to_edit] = Preset(new_cam_angle, new_microphone_direction)
    def get_preset_list(self):
        return list(self.preset_locations.keys())
    def get_preset_info(self, to_get):
        assert to_get in self.preset_locations

        return (self.preset_locations[to_get].camera_angle, 
                self.preset_locations[to_get].microphone_direction)    
