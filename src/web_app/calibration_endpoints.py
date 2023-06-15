from time import sleep
from flask import make_response, jsonify
from web_app.integration import GeneralController
from avonic_camera_api.camera_adapter import ResponseCode


def success():
    return make_response(jsonify({}), 200)

def get_number_of_speaker_points(integration: GeneralController):
    return make_response(jsonify({
        "speaker-points-length": len(integration.audio_model.calibration.speaker_points)
    }), 200)

def add_calibration_speaker(integration: GeneralController):
    """ Adds a speaker point to the calibration. This includes
        both a camera and a microphone direction.

        params:
            integration: the GeneralController instance that has
                a Calibration instance.
    """
    timeouts = 0  # this variable is here to not create an infinite loop in case microphone or camera fail
    mic_dir = ""
    while isinstance(mic_dir, str):
        print("IN WHILE LOOP MIC")
        mic_dir = wait_for_speaker(integration)
        timeouts += 1
        if timeouts > 100:
            return make_response(jsonify({"message": "Could not get direction from the microphone!"}, 504))
    timeouts = 0
    cam_dir = ResponseCode.ACK
    while isinstance(cam_dir, ResponseCode):
        print("IN WHILE LOOP CAM")
        cam_dir = integration.cam_api.get_direction()
        timeouts += 1
        if timeouts > 100:
            return make_response(jsonify({"message": "Could not get direction from the camera!"}, 504))
    
    print("RESULT TO SPEAKER POINT", cam_dir, mic_dir)

    integration.audio_model.calibration.add_speaker_point((cam_dir, mic_dir))
    return success()


def add_calibration_to_mic(integration: GeneralController):
    """ Adds a vector from the camera to the microphone to
        calibration.

        params:
            integration: the GeneralController instance that has
                a Calibration instance.
    """

    cam_dir = integration.cam_api.get_direction()
    integration.audio_model.calibration.add_direction_to_mic(cam_dir)
    integration.audio_model.calibration.calculate_distance()
    return success()


def reset_calibration(integration: GeneralController):
    integration.audio_model.calibration.reset_calibration()
    return success()


def is_calibrated(integration: GeneralController):
    """ Checks whether the current instance of Calibration
        has the necessary vectors to calculate a vector
        from the microphone to the camera.

        params:
            integration: the GeneralController instance that has
                a Calibration instance.
    """
    return make_response(jsonify({
        "is_set": integration.audio_model.calibration.is_calibrated()
    }), 200)


def wait_for_speaker(integration: GeneralController):
    waited_for = 0
    while not integration.mic_api.is_speaking():
        sleep(0.1)
        waited_for += 1
        if waited_for > 50:
            print("Nobody spoke for 5 seconds. Skipping.")
            break
    return integration.mic_api.get_direction()


def get_calibration(integration: GeneralController):
    """ Calls the method in Calibration to calculate the
        vector from the microphone to the camera.

        params:
            integration: the GeneralController instance that has
                a Calibration instance.

        returns:
            camera-coordinates: the coordinates of the camera
                relative to the microphone.
    """
    if integration.audio_model.calibration.is_calibrated():
        integration.audio_model.calibration.calculate_distance()
    return make_response(jsonify({
        "camera-coords": list(integration.audio_model.calibration.mic_to_cam)
    }), 200)
