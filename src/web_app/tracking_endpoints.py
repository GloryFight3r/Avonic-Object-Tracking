from avonic_speaker_tracker.object_model.model_one.STModelOne import HybridTracker
import numpy as np
from avonic_speaker_tracker.preset_model.PresetModel import PresetModel
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel
from avonic_speaker_tracker.object_model.model_two.WaitObjectAudioModel import WaitObjectAudioModel
from avonic_speaker_tracker.audio_model.AudioModelNoAdaptiveZoom import AudioModelNoAdaptiveZoom
from flask import make_response, jsonify, request
from avonic_speaker_tracker.updater import UpdateThread
from web_app.integration import GeneralController, ModelCode
from avonic_speaker_tracker.object_model.yolov8 import YOLOPredict

def start_thread_endpoint(integration: GeneralController):
    """ This method starts the thread that controlls the actual tracking and calls 
    the corresponding tracking model depending on the user's choice.
    """
    # start (unpause) the thread
    if (integration.thread is None) or (integration.event.value == 0):
        integration.event.value = 1
        if integration.preset.value == ModelCode.PRESET:
            model = PresetModel(integration.cam_api, integration.mic_api,
                                    filename=integration.filepath + "presets.json")
        elif integration.preset.value == ModelCode.AUDIO:
            model = AudioModel(integration.cam_api, integration.mic_api,
                                    filename=integration.filepath + "calibration.json")
        elif integration.preset.value == ModelCode.AUDIONOZOOM:
            model = AudioModelNoAdaptiveZoom(integration.cam_api, integration.mic_api,
                                    filename = integration.filepath + "calibration.json")
        elif integration.preset.value == ModelCode.HYBRID:
            model = HybridTracker(integration.cam_api, integration.mic_api, integration.nn, integration.footage_thread,
                                  integration.filepath + "calibration.json")
        else:
            if integration.nn is None:
                integration.nn = YOLOPredict()

            model = WaitObjectAudioModel(
                integration.cam_api, integration.mic_api,
                integration.resolution,
                5, integration.nn, integration.footage_thread,
                filename=integration.filepath + "calibration.json")

        integration.thread = UpdateThread(integration.event,
                                          integration.cam_api, integration.mic_api,
                                          model, integration.filepath)
        integration.event.value = 1

        integration.info_threads_event.value = 1
        integration.thread.start()
        return make_response(jsonify({}), 200)
    else:
        print("Thread already running!")
        return make_response(jsonify({}), 403)


def stop_thread_endpoint(integration: GeneralController):
    """ Stops(pauses) the thread that controlls the tracking 
    """
    integration.event.value = 0
    integration.info_threads_event.value = 0

    if integration.thread is not None:
        integration.thread.join()
    return make_response(jsonify({}), 200)


def update_microphone(integration: GeneralController):
    """ Updates the new microphone data in the corresponding field in the WebUI
    """
    data = request.get_json()
    integration.ws.emit('microphone-update', data)
    return make_response(jsonify({}), 200)


def update_camera(integration: GeneralController):
    """ Updates the new camera data in the corresponding field in the WebUI
    """
    data = request.get_json()
    integration.ws.emit('camera-update', data)
    return make_response(jsonify({}), 200)


def update_calibration(integration: GeneralController):
    """ Updates the new calibration data in the corresponding field in the WebUI
    """
    data = request.get_json()
    integration.ws.emit('calibration-update', data)
    return make_response(jsonify({}), 200)


def is_running_endpoint(integration: GeneralController):
    """ Returns: Whether the thread that controlls the tracking is currently running
    """
    return make_response(
        jsonify({"is-running": integration.thread and integration.thread.is_alive()}))

def track_presets(integration: GeneralController):
    """ Sets the current tracking model to PresetModel
    """
    integration.preset.value = ModelCode.PRESET
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_hybrid(integration: GeneralController):
    integration.preset.value = ModelCode.HYBRID
    print(integration.preset.value)
    return make_response(jsonify({"hybrid":integration.preset.value}), 200)

def track_continuously(integration: GeneralController):
    """ Sets the current tracking model to the AudioModel
    """
    integration.preset.value = ModelCode.AUDIO
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_object_continuously(integration: GeneralController):
    """ Sets the current tracking model to ObjectModel
    """
    integration.preset.value = ModelCode.OBJECT
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_continuously_without_adaptive_zooming(integration: GeneralController):
    """ Sets the current tracking model to AudioModelNoAdaptiveZoom
    """
    integration.preset.value = ModelCode.AUDIONOZOOM
    print(integration.preset.value)
    #                        TODO preset?
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def preset_use(integration: GeneralController):
    if integration.preset.value == 1:
        integration.preset.value = 0
    else:
        integration.preset.value = 1
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)
