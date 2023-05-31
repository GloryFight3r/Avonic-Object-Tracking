from time import sleep
from flask import make_response, jsonify, request
from web_app.integration import GeneralController, verify_address


def address_set_microphone_endpoint(integration: GeneralController):
    try:
        addr = (request.form["ip"], int(request.form["port"]))
        verify_address(addr)
        ret_msg, code = integration.mic_api.set_address(addr)
        if code:
            ret_code = 200
        else:
            ret_code = 400
        return make_response(jsonify(ret_msg), ret_code)
    except (AssertionError, ValueError):
        return make_response(jsonify({"message": "Invalid address!"}), 400)

def height_set_microphone_endpoint(integration: GeneralController):
    integration.calibration.set_height(float(request.form["microphone-height"]))
    return make_response(jsonify(
        {"microphone-height": integration.calibration.mic_height}), 200)


def direction_get_microphone_endpoint(integration: GeneralController):
    ret = integration.mic_api.get_direction()
    if isinstance(ret, str):
        return make_response(jsonify({"message": ret}), 504)
    return make_response(jsonify({"microphone-direction": list(ret)}), 200)


def speaking_get_microphone_endpoint(integration: GeneralController):
    ret = integration.mic_api.is_speaking()
    if isinstance(ret, str):
        return make_response(jsonify({"message": ret}), 504)
    return make_response(jsonify({"microphone-speaking": ret}), 200)


def get_speaker_direction_endpoint(integration: GeneralController):
    ret = wait_for_speaker(integration)
    if isinstance(ret, str):
        return make_response(jsonify({"message": ret}), 504)
    return make_response(jsonify({"microphone-direction": list(ret)}), 200)


def wait_for_speaker(integration: GeneralController):
    while not integration.mic_api.is_speaking():
        sleep(0.1)
    return integration.mic_api.get_direction()
