from flask import make_response, jsonify
from web_app.integration import GeneralController
import numpy as np

def success():
    return make_response(jsonify({}), 200)

def add_calibration_speaker(integration: GeneralController):
    mic_dir = integration.mic_api.vector()
    cam_dir = integration.cam_api.get_saved_direction()

    integration.calibration.add_speaker_point((cam_dir, mic_dir))
    return success()

def add_calibration_to_mic(integration: GeneralController):
    cam_dir = integration.cam_api.get_direction()
    integration.calibration.add_direction_to_mic(cam_dir)
    return success()

def reset_calibration(integration: GeneralController):
    integration.calibration.reset_calibration()
    return success()

def is_calibrated(integration: GeneralController):
    return make_response(jsonify({
        "is_set": integration.calibration.is_calibrated()
    }), 200)

def get_calibration(integration: GeneralController):
    cam_coord = np.array([0.0, 0.0, 0.0])
    if integration.calibration.is_calibrated():
        cam_coord = integration.calibration.calculate_distance()

    return make_response(jsonify({
        "camera-coords": list(cam_coord)
    }), 200)
