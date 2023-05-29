import numpy as np

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.converter import vector_angle
from avonic_speaker_tracker.preset_control import find_most_similar_preset
from avonic_speaker_tracker.preset import PresetCollection
from avonic_speaker_tracker.calibration import Calibration
from avonic_speaker_tracker.coordinate_translation import translate_microphone_to_camera_vector
from microphone_api.microphone_control_api import MicrophoneAPI

def preset_pointer(mic_api: MicrophoneAPI,
          preset_locations: PresetCollection):
    """ Calculates the direction to which the camera should point so that
        it is the closest to an existing preset.
        Args:
            mic_api: The controller for the microphone 
            preset_locations: Collection containing all current presets 
        Returns: the vector in which direction the camera should point
    """
    preset_names = np.array(preset_locations.get_preset_list())
    presets_mic = []
    for i in range(len(preset_names)):
        presets_mic.append(preset_locations.get_preset_info(preset_names[i])[1])
    mic_direction = mic_api.get_direction()
    preset_id = find_most_similar_preset(mic_direction,presets_mic)
    preset = preset_locations.get_preset_info(preset_names[preset_id])
    direct = [int(np.rad2deg(preset[0][0])), int(np.rad2deg(preset[0][1])),0]
    return direct

def continuous_pointer(mic_api: MicrophoneAPI, calibration: Calibration):
    """ Calculates the direction of the camera so it point to the speaker.
        Args: 
            mic_api: The controller for the microphone 
            calibration: Information on the calibration of the system
        Returns: the pitch and yaw of the camera and the zoom value
    """
    mic_direction = mic_api.get_direction()

    cam_vec = translate_microphone_to_camera_vector(calibration.to_mic_direction,mic_direction,calibration.mic_height)

    cam_vec = [-cam_vec[0], cam_vec[1], cam_vec[2]]


    direct = vector_angle(cam_vec)
    direct = [int(np.rad2deg(direct[0])),int(np.rad2deg(direct[1])),0]
    return direct


def point(cam_api: CameraAPI, mic_api: MicrophoneAPI, preset_locations: PresetCollection, preset_use: bool, calibration: Calibration, prev_dir=None):
    """ Points the camera towards the calculated direction from either: 
    the presets or the continuous follower.
        Args: 
            cam_api: The controller for the camera
            mic_api: The controller for the microphone
            preset_locations: Collection containing all current presets 
            preset_use: True if we are using presets and false otherwise
            calibration: Information on the calibration of the system
            prev_dir: The previous direction to which the camera was pointing
        Returns: the pitch and yaw of the camera and the zoom value
    """
    if prev_dir is None:
        prev_dir = [0.0, 0.0, 0.0]
    direct = [0.0, 0.0, 0.0]

    if preset_use == True:
        direct = preset_pointer(mic_api, preset_locations)
    else :
        direct = continuous_pointer(mic_api, calibration)
    if prev_dir[0] != direct[0] or prev_dir[1] != direct[1]:
        cam_api.move_absolute(24,20, direct[0], direct[1])
        if preset_use == True:
            cam_api.direct_zoom(direct[2])
        prev_dir = direct

    return direct
