import numpy as np
from flask import make_response, jsonify, request

from avonic_camera_api.converter import angle_vector
from microphone_api.microphone_control_api import MicrophoneAPI

def height_set_microphone_endpoint(mic_api: MicrophoneAPI):
    mic_api.set_height(float(request.get_json()["microphoneHeight"]))
    return make_response(jsonify({"microphone-height" : mic_api.microphone.height}), 200)

def direction_get_microphone_endpoint(mic_api: MicrophoneAPI):
    azimuth = mic_api.get_azimuth(30)
    elevation = mic_api.get_elevation(30)

    vec = angle_vector(np.deg2rad(azimuth), np.deg2rad(elevation))
    return make_response(jsonify(vec.tolist()), 200)