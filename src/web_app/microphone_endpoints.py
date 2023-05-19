from flask import make_response, jsonify, request
from web_app.integration import GeneralController
#from web_app.general_endpoints import wait_for_speaker


def height_set_microphone_endpoint(integration: GeneralController):
    integration.calibration.set_height(float(request.form["microphone-height"]))
    return make_response(jsonify({"microphone-height": integration.calibration.mic_height}), 200)

def direction_get_microphone_endpoint(integration: GeneralController):
    return make_response(jsonify({"microphone-direction": list(integration.mic_api.get_direction())}), 200)

def speaking_get_microphone_endpoint(integration: GeneralController):
    return make_response(jsonify({"microphone-speaking": integration.mic_api.is_speaking()}), 200)

def get_speaker_direction_endpoint(integration: GeneralController):
    return make_response(jsonify({"microphone-direction" : list(wait_for_speaker(integration)) }), 200)

def wait_for_speaker(integration: GeneralController):
    while not integration.mic_api.is_speaking():
        sleep(0.1)
    return integration.mic_api.get_direction()
