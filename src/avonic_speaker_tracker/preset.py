import json
import numpy as np


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.ndarray, np.generic)):
            return obj.tolist()
        return obj.__dict__
    

class Preset:
    def __init__(self, camera_angle: np.ndarray, microphone_direction: np.ndarray):
        self.camera_angle = camera_angle
        self.microphone_direction = microphone_direction

class PresetCollection:
    preset_locations = {}
    filename = None
    def __init__(self, filename=None):
        self.filename = filename
        self.preset_locations = {}
        if filename is not None:
            self.load()

    def add_preset(self, to_add: str,
        cam_angle: np.ndarray, microphone_direction: np.ndarray) -> None:
        """ Adds a preset to the dictionary of presets with the given name

        Args:
            to_add: Name of the preset
            cam_angle: Angle of the camera
            microphone_direction: Direction of the speaker
        """
        assert to_add not in self.preset_locations
        self.preset_locations[to_add] = Preset(cam_angle, microphone_direction)
        self.record()

    def remove_preset(self, to_remove: str):
        """ Removes a preset from the dictionary of presets with the given name

        Args:
            to_remove: Name of the preset
        """
        assert to_remove in self.preset_locations
        del self.preset_locations[to_remove]
        self.record()

    def edit_preset(self, to_edit: str,
        new_cam_angle: np.ndarray, new_microphone_direction: np.ndarray):
        """ Edits a preset with the given name only
        if it is already inside the dictionary

        Args:
            to_edit: Name of the preset
            new_cam_angle: Angle of the camera
            new_microphone_direction: Direction of the speaker
        """
        assert to_edit in self.preset_locations
        self.preset_locations[to_edit] = Preset(new_cam_angle, new_microphone_direction)
        self.record()

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

    def record(self):
        if self.filename is not None:
            with open(self.filename, "w") as outfile:
                outfile.write(json.dumps(self.preset_locations, indent=4, cls=CustomEncoder))
    
    def load(self):
        if self.filename is not None:
            try:
                f = open(self.filename)
                f.close()
            except:
                with open(self.filename, "x") as outfile:
                    outfile.write(json.dumps({}, indent=4, cls=CustomEncoder))
            f = open(self.filename)
            data = json.load(f)
            print(data)
            self.preset_locations = {}
            for key in data:
                self.preset_locations[key] = Preset(np.array(data[key]["camera_angle"]), np.array(data[key]["microphone_direction"]))
            print(self.preset_locations)
            f.close()
