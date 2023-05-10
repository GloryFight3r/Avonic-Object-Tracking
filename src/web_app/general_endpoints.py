from flask import make_response, jsonify, request
from avonic_camera_api.converter import angle_vector
from web_app.integration import GeneralController
from time import sleep

import numpy as np

def success():
    return make_response(jsonify({}), 200)

def add_calibration_position(integration: GeneralController):
    #while not integration.mic_api.is_speaking():
    #    sleep(0.1)
    mic_dir = integration.mic_api.get_direction()
    cam_dir = integration.cam_api.get_direction()

    integration.environment.add_point_to_plane((cam_dir, mic_dir))
    count = len(integration.environment.plane.points)
    return success()

def get_calibration_count(integration: GeneralController):
    count = len(integration.environment.plane.points)
    return make_response(jsonify({"count": count}), 200)
