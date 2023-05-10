from flask import make_response, jsonify, request

from microphone_api.microphone_control_api import MicrophoneAPI
from web_app import GeneralController

def height_set_microphone_endpoint(integration: GeneralController):
    integration.mic_api.set_height(float(request.get_json()["microphoneHeight"]))
    return make_response(jsonify({"microphone-height": integration.mic_api.height}), 200)


def direction_get_microphone_endpoint(integration: GeneralController):
    return make_response(jsonify({"microphone-direction": list(integration.mic_api.get_direction())}), 200)


def speaking_get_microphone_endpoint(integration: GeneralController):
    return make_response(jsonify({"microphone-speaking": integration.mic_api.is_speaking()}), 200)
