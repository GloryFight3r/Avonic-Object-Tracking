import json
import numpy as np
from avonic_speaker_tracker.utils.persistency_utils import CustomEncoder


class Preset:
    """ This class contains all the information about a given preset. 
    This information is the camera direction towards the speaker and 
    the direction from the microphone towards the speaker. 
    """
    def __init__(self, camera_info: np.ndarray, microphone_direction: np.ndarray):
        """ Constructor for the preset
            Args:
                camera_info: the direction from the camera towards the speaker and the zoom
                microphone_direction: the direction from the microphone towards the speaker
        """
        self.camera_info: np.ndarray = camera_info
        self.microphone_direction: np.ndarray = microphone_direction

    def __str__(self):
        return f"Preset({self.camera_info}, {self.microphone_direction})"

class PresetCollection:
    """ This class is a container for all the existing presets.
    """
    preset_locations = {}
    filename = None
    
    default_camera_info: list[float] = [0.0, 0.0, 1.0]
    default_mic_info: list[float] = [0.0, 1.0, 0.0]
    def __init__(self, filename: str = ""):
        """ Constructor which loads an existing file containing presets.
        """
        self.filename: str = filename
        self.preset_locations: dict[str, Preset] = {}
        self.load()

    def add_preset(self, to_add: str,
                   cam_info: np.ndarray, microphone_direction: np.ndarray) -> None:
        """ Adds a preset to the dictionary of presets with the given name

        Args:
            to_add: Name of the preset
            cam_info: Angle + zoom of the camera
            microphone_direction: Direction of the speaker
        """
        assert to_add not in self.preset_locations
        assert isinstance(cam_info, np.ndarray) and len(cam_info) == 3
        assert isinstance(microphone_direction, np.ndarray) and len(microphone_direction) == 3
        self.preset_locations[to_add] = Preset(cam_info, microphone_direction)
        self.record()

    def remove_preset(self, to_remove: str) -> None:
        """ Removes a preset from the dictionary of presets with the given name

        Args:
            to_remove: Name of the preset
        """
        assert to_remove in self.preset_locations
        del self.preset_locations[to_remove]
        self.record()

    def edit_preset(self, to_edit: str,
        new_cam_info: np.ndarray, new_microphone_direction: np.ndarray) -> None:
        """ Edits a preset with the given name only if it is already inside the dictionary

        Args:
            to_edit: Name of the preset
            new_cam_info: Angle of the camera
            new_microphone_direction: Direction of the speaker
        """
        assert to_edit in self.preset_locations
        assert isinstance(new_cam_info, np.ndarray) and len(new_cam_info) == 3
        assert isinstance(new_microphone_direction, np.ndarray) and len(new_microphone_direction) == 3
        self.preset_locations[to_edit] = Preset(new_cam_info, new_microphone_direction)
        self.record()

    def get_preset_list(self) -> list[str]:
        """ Returns a list with the names of the presets

        Returns: List with presets names

        """
        return list(self.preset_locations.keys())

    def get_preset_info(self, to_get: str) -> tuple[np.ndarray, np.ndarray]:
        """ Returns the camera angle and microphone direction for a preset with a given name

        Args:
            to_get: Name of the preset

        Returns: Camera angle and microphone direction for the given preset

        """
        assert to_get in self.preset_locations
        return (self.preset_locations[to_get].camera_info,
                self.preset_locations[to_get].microphone_direction)

    def record(self) -> None:
        """ Records the existing presets in the corresponfing file
        """
        if self.filename != "":
            with open(self.filename, "w", encoding="utf-8") as outfile:
                outfile.write(json.dumps(self.preset_locations, indent=4, cls=CustomEncoder))

    def load(self) -> None:
        """ Loads existing presets from the corresponding file
        """
        if self.filename != "":
            try:
                with open(self.filename, encoding="utf-8") as f:
                    print("Loading json...")
            except FileNotFoundError:
                with open(self.filename, "x", encoding="utf-8") as outfile:
                    print("Create new preset json...")
                    outfile.write(json.dumps({}, indent=4, cls=CustomEncoder))
            with open(self.filename, encoding="utf-8") as f:
                data = json.load(f)
                self.preset_locations = {}
                for key in data:
                    try:
                        self.preset_locations[key] = Preset(np.array(data[key]["camera_info"]),
                            np.array(data[key]["microphone_direction"]))
                        if len(data[key]["camera_info"]) != 3:
                            self.preset_locations[key].camera_info = \
                                np.array(PresetCollection.default_camera_info)
                            print("Setting camera_info in one of the presets to default value")
                        if len(data[key]["microphone_direction"]) != 3:
                            self.preset_locations[key].microphone_direction = \
                                np.array(PresetCollection.default_mic_info)
                            print("Setting microphone_direction in " +
                                "one of the presets to default value")
                    except Exception as e:
                        print(e)
                        self.preset_locations[key] = Preset(
                            np.array(PresetCollection.default_camera_info),
                            np.array(PresetCollection.default_mic_info))
                        print("Setting one of the presets to default values")
                print("Loaded presets: ", self.preset_locations)
            self.record()

    def set_filename(self, filename: str):
        """ Setter for the location of the file containing the presets
        """
        self.filename = filename
        self.load()
