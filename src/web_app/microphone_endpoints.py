from flask import make_response, jsonify, request
from web_app.integration import GeneralController


def height_set_microphone_endpoint(integration: GeneralController):
    integration.mic_api.set_height(float(request.form["microphone-height"]))
    return make_response(jsonify({"microphone-height": integration.mic_api.height}), 200)


def direction_get_microphone_endpoint(integration: GeneralController):
    return make_response(jsonify({"microphone-direction": list(integration.mic_api.get_direction())}), 200)


def speaking_get_microphone_endpoint(integration: GeneralController):
    return make_response(jsonify({"microphone-speaking": integration.mic_api.is_speaking()}), 200)
