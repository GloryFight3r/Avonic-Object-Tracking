from web_app.integration import GeneralController
from flask import make_response, jsonify, request
import numpy as np

def success():
    return make_response(jsonify({}), 200)

def add_preset_location(integration: GeneralController):
    data = request.form
    print(data)
    try:
        camera_angles = np.array([
            float(data["camera-direction-alpha"]),
            float(data["camera-direction-beta"])
        ])
        microphone_direction = np.array([
            float(data["mic-direction-x"]), 
            float(data["mic-direction-y"]),
            float(data["mic-direction-z"])
        ])
        integration.preset_locations.add_preset(camera_angles, microphone_direction)
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()

def edit_preset_location(integration: GeneralController):
    data = request.form
    try:
        camera_angles = np.array([
            float(data["camera-direction-alpha"]),
            float(data["camera-direction-beta"])
        ])
        microphone_direction = np.array([
            float(data["mic-direction-x"]), 
            float(data["mic-direction-y"]),
            float(data["mic-direction-z"])
        ])
        integration.preset_locations.edit_preset(int(data["preset-select"]), camera_angles, microphone_direction)
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()

def remove_preset_location(integration: GeneralController):
    data = request.form
    try:
        integration.preset_locations.remove_preset(int(data["preset-select"]))
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()

