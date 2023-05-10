from flask import make_response, jsonify, request
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_camera_api.converter import angle_vector

import numpy as np

def success():
    return make_response(jsonify({}), 200)

def add_calibration_position(cam_api: CameraAPI, mic_api: MicrophoneAPI):
    cam_dir = cam_api.get_direction()
    azimuth = mic_api.get_azimuth(30)
    elevation = mic_api.get_elevation(30)
    vec = angle_vector(np.deg2rad(azimuth), np.deg2rad(elevation))
    print(cam_dir, vec)
    return success()
