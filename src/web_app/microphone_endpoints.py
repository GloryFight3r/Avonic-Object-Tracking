import time
from flask import make_response, jsonify, request
from web_app.integration import GeneralController, verify_address


def address_set_microphone_endpoint(integration: GeneralController):
    """ Endpoint that sends a request to set the address of the microphone.
    """
    try:
        addr = (request.form["microphone-ip"], int(request.form["microphone-port"]))
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
    """ Endpoint that sends a request to set the height of the microphone.
    """
    integration.audio_model.calibration.set_height(float(request.form["microphone-height"]))
    return make_response(jsonify(
        {"microphone-height": integration.audio_model.calibration.mic_height}), 200)


def direction_get_microphone_endpoint(integration: GeneralController):
    """ Endpoint that sends a request to get the current direction from the microphone.
    """
    ret = integration.mic_api.get_direction()
    if isinstance(ret, str):
        return make_response(jsonify({"message": ret}), 504)
    return make_response(jsonify({"microphone-direction": list(ret)}), 200)


def speaking_get_microphone_endpoint(integration: GeneralController):
    """ Endpoint that sends a request to get information if someone is currently speaking.
    """
    ret = integration.mic_api.is_speaking()
    if isinstance(ret, str):
        return make_response(jsonify({"message": ret}), 504)
    return make_response(jsonify({"microphone-speaking": ret}), 200)


def get_speaker_direction_endpoint(integration: GeneralController):
    """ Endpoint that sends a request to get the current direction 
        from the microphone but waits for someone to speak.
    """
    ret = wait_for_speaker(integration)
    if isinstance(ret, str):
        return make_response(jsonify({"message": ret}), 504)
    return make_response(jsonify({"microphone-direction": list(ret)}), 200)


def wait_for_speaker(integration: GeneralController):
    """ Waits for the speaker to speak in order to get the direction 
    from the microphone towards him

    Args:
        integration: The controller object

    Returns:
        Direction towards the speaker

    """
    approaching_limit: int = 0
    while not integration.mic_api.is_speaking() and approaching_limit < 10:
        approaching_limit += 1
        time.sleep(0.1)
    return integration.mic_api.get_direction()
