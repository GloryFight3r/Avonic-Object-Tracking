import numpy as np

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_speaker_tracker.preset_control import find_most_similar_preset
from avonic_speaker_tracker.preset import PresetCollection
from microphone_api.microphone_control_api import MicrophoneAPI


def point(cam_api: CameraAPI,
    mic_api: MicrophoneAPI, preset_locations: PresetCollection, prev_dir=None):
    if prev_dir is None:
        prev_dir = [0.0, 0.0]
    preset_names = np.array(preset_locations.get_preset_list())
    presets_mic = []
    for i in range(len(preset_names)):
        presets_mic.append(preset_locations.get_preset_info(preset_names[i])[1])
    mic_direction = mic_api.get_direction()
    preset_id = find_most_similar_preset(mic_direction,presets_mic)
    preset = preset_locations.get_preset_info(preset_names[preset_id])
    if prev_dir[0] != int(np.rad2deg(preset[0][0])) or prev_dir[1] != int(np.rad2deg(preset[0][1])):
        cam_api.move_absolute(24, 20,
                            int(np.rad2deg(preset[0][0])), int(np.rad2deg(preset[0][1])))
        prev_dir = [int(np.rad2deg(preset[0][0])), int(np.rad2deg(preset[0][1]))]
    return prev_dir
