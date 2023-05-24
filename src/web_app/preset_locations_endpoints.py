import numpy as np
from flask import make_response, jsonify, request
from web_app.integration import GeneralController
from avonic_speaker_tracker.pointer import point


def success():
    return make_response(jsonify({}), 200)


def add_preset_location(integration: GeneralController):
    """ Adds a preset location using the data from the request

    Args:
        integration: The controller containing all the dependencies

    Returns: A http response which indicates success(200) or failure(400)
        
    """
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
        integration.preset_locations.add_preset(data["preset-name"],\
             camera_angles, microphone_direction)
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()


def edit_preset_location(integration: GeneralController):
    """ Edits the preset using the new data from the request

    Args:
        integration: The controller containing all the dependencies

    Returns: A http response which indicates success(200) or failure(400)

    """
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
        integration.preset_locations.edit_preset(data["preset-name"],\
            camera_angles, microphone_direction)
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()


def remove_preset_location(integration: GeneralController):
    """ Removes the preset using the new index from the request

    Args:
        integration: The controller containing all the dependencies

    Returns: A http response which indicates success(200) or failure(400)

    """
    data = request.form
    try:
        integration.preset_locations.remove_preset(data["preset-name"])
    except AssertionError:
        return make_response(jsonify({}), 400)
    return success()


def get_preset_list(integration: GeneralController):
    """ Gets the

    Args:
        integration: The controller containing all the dependencies

    Returns: A http response which indicates success(200) or failure(400)

    """
    return make_response(
        jsonify({"preset-list":integration.preset_locations.get_preset_list()}
        ), 200)


def get_preset_info(integration: GeneralController, preset_name: str):
    try:
        info = integration.preset_locations.get_preset_info(preset_name)
        return make_response(jsonify({
            "position-alpha-value": info[0][0],
            "position-beta-value": info[0][1],
            "microphone-direction": [info[1][0], info[1][1], info[1][2]],
        }), 200)
    except AssertionError:
        return make_response(jsonify({}), 400)


def point_to_closest_preset(integration: GeneralController):
    point(integration.cam_api, integration.mic_api, integration.preset_locations)
    return make_response(jsonify({}), 200)
