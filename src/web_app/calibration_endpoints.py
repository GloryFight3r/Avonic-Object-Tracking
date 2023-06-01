from flask import make_response, jsonify
from time import sleep
from web_app.integration import GeneralController

def success():
    return make_response(jsonify({}), 200)

def add_calibration_speaker(integration: GeneralController):
    mic_dir = integration.mic_api.vector()
    cam_dir = integration.cam_api.get_saved_direction()

    integration.audio_model.calibration.add_speaker_point((cam_dir, mic_dir))
    return success()

def add_calibration_to_mic(integration: GeneralController):
    cam_dir = integration.cam_api.get_direction()
    integration.audio_model.calibration.add_direction_to_mic(cam_dir)
    integration.audio_model.calibration.calculate_distance()
    return success()

def reset_calibration(integration: GeneralController):
    integration.audio_model.calibration.reset_calibration()
    return success()

def is_calibrated(integration: GeneralController):
    # uncomment this to see the calibration results in the terminal
    #integration.calibration.calculate_distance()
    return make_response(jsonify({
        "is_set": integration.audio_model.calibration.is_calibrated()
    }), 200)

def wait_for_speaker(integration: GeneralController):
    while not integration.mic_api.is_speaking():
        sleep(0.1)
    return integration.mic_api.get_direction()
def get_calibration(integration: GeneralController):
    return make_response(jsonify({
        "camera-coords": list(integration.audio_model.calibration.mic_to_cam)
    }), 200)
