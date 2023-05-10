from flask import make_response, jsonify, request
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.converter import angle_vector
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.environment import Environment
from time import sleep

import numpy as np

def success():
    return make_response(jsonify({}), 200)

def add_calibration_position(cam_api: CameraAPI, mic_api: MicrophoneAPI, env: Environment):
    while not mic_api.is_speaking():
        sleep(0.1)
    mic_dir = mic_api.get_direction()
    cam_dir = cam_api.get_direction()

    env.add_point_to_plane((cam_dir, mic_dir))

    return success()
