from flask import make_response, jsonify, request
from avonic_camera_api.converter import angle_vector
from web_app.integration import GeneralController
from time import sleep

import numpy as np

def success():
    return make_response(jsonify({}), 200)

def add_calibration_speaker(integration: GeneralController):
    #while not integration.mic_api.is_speaking():
    #    sleep(0.1)
    #mic_dir = integration.mic_api.get_direction()
    #cam_dir = integration.cam_api.get_direction()
    while not integration.mic_api.speaking:
        sleep(0.1)

    cam_dir = integration.cam_api.get_direction()
    mic_dir = integration.mic_api.vector()

    integration.calibration.add_speaker_point((cam_dir, mic_dir))
    return success()

def add_calibration_to_mic(integration: GeneralController):
    cam_dir = integration.cam_api.get_direction()
    integration.calibration.add_direction_to_mic(cam_dir)
    return success()

def reset_calibration(integration: GeneralController):
    integration.calibration.reset_calibration()
    return success()

def is_calibrated(integration: GeneralController):
    return make_response(jsonify({
        "is_set": integration.calibration.is_calibrated()
    }), 200)
