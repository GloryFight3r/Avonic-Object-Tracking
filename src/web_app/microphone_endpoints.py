from flask import make_response, jsonify, request

from microphone_api.microphone_control_api import MicrophoneAPI


def height_set_microphone_endpoint(mic_api: MicrophoneAPI):
    mic_api.set_height(float(request.form["microphoneHeight"]))
    return make_response(jsonify({"microphone-height": mic_api.height}), 200)


def direction_get_microphone_endpoint(mic_api: MicrophoneAPI):
    return make_response(jsonify({"microphone-direction": list(mic_api.get_direction())}), 200)


def speaking_get_microphone_endpoint(mic_api: MicrophoneAPI):
    return make_response(jsonify({"microphone-speaking": mic_api.is_speaking()}), 200)
