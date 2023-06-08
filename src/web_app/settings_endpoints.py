from flask import make_response, jsonify, request
import web_app.camera_endpoints
from web_app.integration import GeneralController


def get(integration: GeneralController):
    """
    Get the current settings

    Returns:
        The current settings in json format
    """
    cam_addr = integration.cam_api.camera.address
    mic_addr = integration.mic_api.sock.address

    ret = {
        "camera-ip": cam_addr[0],
        "camera-port": cam_addr[1],
        "microphone-ip": mic_addr[0],
        "microphone-port": mic_addr[1],
        "microphone-thresh": integration.mic_api.threshold,
        "filepath": integration.filepath
    }

    return make_response(jsonify(ret), 200)


def set_settings(integration: GeneralController):
    """
    Set a new set of settings

    Returns:
        200 on success, 400 on failure (invalid data provided)
    """
    camera_response = web_app.camera_endpoints.address_set_camera_endpoint(integration)
    if camera_response.status_code != 200:
        return camera_response
    microphone_response = web_app.microphone_endpoints.address_set_microphone_endpoint(integration)
    if microphone_response.status_code != 200:
        return microphone_response
    try:
        data = request.form
        integration.mic_api.threshold = int(data["microphone-thresh"])
        filepath = data["filepath"]
        if filepath is None:
            filepath = ""
        integration.filepath = str(filepath)
        if integration.save():
            return make_response(jsonify({}), 200)
        return make_response(jsonify(
            {"message": "Something went wrong while saving settings file! Check application output!"}), 500)
    except (ValueError, KeyError):
        return make_response(jsonify({"message": "Invalid threshold or filepath."}), 400)
