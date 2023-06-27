import os
import signal
import time
from flask import make_response, jsonify, request
import maat_web_app.camera_endpoints
from maat_web_app.integration import GeneralController


def get(integration: GeneralController):
    """
    Get the current settings

    Returns:
        The current settings in json format
    """
    cam_addr = integration.cam_api.camera.address
    cam_http_port = integration.cam_api.camera_http.address[1]
    mic_addr = integration.mic_api.sock.address

    ret = {
        "camera-ip": cam_addr[0],
        "camera-port": cam_addr[1],
        "camera-http-port": cam_http_port,
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
    camera_response = maat_web_app.camera_endpoints.address_set_camera_endpoint(integration)
    if camera_response.status_code != 200:
        return camera_response
    microphone_response = maat_web_app.microphone_endpoints.address_set_microphone_endpoint(integration)
    if microphone_response.status_code != 200:
        return microphone_response
    saved = False
    try:
        data = request.form
        integration.mic_api.threshold = int(data["microphone-thresh"])
        filepath = data["filepath"]
        if filepath is None or len(filepath) < 1:
            integration.filepath = ""
        else:
            integration.filepath = str(filepath)
            if integration.filepath[-1] != "/":
                integration.filepath += "/"
        integration.audio_model.set_filename(integration.filepath + "calibration.json")
        integration.preset_model.set_filename(integration.filepath + "presets.json")

        saved = integration.save()
        if saved:
            return make_response(jsonify({}), 200)
        return make_response(jsonify(
            {"message": "Something went wrong while saving " +
                        "settings file! Check application output!"}),
            500)
    except (ValueError, KeyError):
        return make_response(jsonify({"message": "Invalid threshold or filepath."}), 400)
    finally:
        if saved and integration.testing.value == 0:  # do not exit when testing
            print("Restarting server...")
            integration.footage_thread_event.value = 0
            time.sleep(1)
            try:
                if integration.footage_pid.value > 1:
                    os.kill(integration.footage_pid.value, signal.SIGINT)  # pragma: no mutate
            except ProcessLookupError:
                pass  # don't care mate
            os.kill(integration.pid.value, signal.SIGINT)  # pragma: no mutate
