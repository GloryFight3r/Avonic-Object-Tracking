from avonic_speaker_tracker.preset_control import find_most_similar_preset
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.preset import PresetCollection
from avonic_speaker_tracker.calibration import Calibration
from avonic_speaker_tracker.coordinate_translation import translate_microphone_to_camera_vector
from avonic_camera_api.converter import vector_angle
import numpy as np

def preset_pointer(mic_api: MicrophoneAPI, preset_locations: PresetCollection, prev_dir):
    dir = [0.0, 0.0]
    preset_names = np.array(preset_locations.get_preset_list())
    presets_mic = []
    for i in range(len(preset_names)):
        presets_mic.append(preset_locations.get_preset_info(preset_names[i])[1])
    mic_direction = mic_api.get_direction()
    preset_id = find_most_similar_preset(mic_direction,presets_mic)
    preset = preset_locations.get_preset_info(preset_names[preset_id])
    dir = [int(np.rad2deg(preset[0][0])), int(np.rad2deg(preset[0][1]))]
    return dir

def continuous_pointer(mic_api: MicrophoneAPI, calibration: Calibration, prev_dir):
    print("continuous")
    mic_direction = mic_api.get_direction()

    cam_vec = translate_microphone_to_camera_vector(calibration.to_mic_direction,mic_direction,calibration.mic_height)

    dir = vector_angle(cam_vec)
    print(dir)
    return dir


def point(cam_api: CameraAPI, mic_api: MicrophoneAPI, preset_locations: PresetCollection, preset_use: bool, calibration: Calibration, prev_dir=None):
    if prev_dir is None:
        prev_dir = [0.0, 0.0]
    dir = [0.0, 0.0]

    print("pointer")
    if preset_use == True:
        dir = preset_pointer(mic_api, preset_locations, prev_dir)
    else :
        dir = continuous_pointer(mic_api, calibration,prev_dir)
    if prev_dir[0] != dir[0] or prev_dir[1] != dir[1]:
        cam_api.move_absolute(24,20, dir[0], dir[1])
        prev_dir = dir

    return dir 

    
