import numpy as np

class Preset:
    def __init__(self, camera_angle:np.ndarray, microphone_direction:np.ndarray):
        self.camera_angle = camera_angle
        self.microphone_direction = microphone_direction

class PresetCollection:
    def __init__(self):
        self.preset_locations = dict()
        self.counter = 1

    def add_preset(self, cam_angle, microphone_direction):
        print(cam_angle, microphone_direction)
        self.preset_locations[self.counter] = Preset(cam_angle, microphone_direction)
        self.counter += 1
    def remove_preset(self, to_remove):
        del self.preset_locations[to_remove]
    def edit_preset(self, to_edit, new_cam_angle, new_microphone_direction):
        self.preset_locations[to_edit] = Preset(new_cam_angle, new_microphone_direction)
    
