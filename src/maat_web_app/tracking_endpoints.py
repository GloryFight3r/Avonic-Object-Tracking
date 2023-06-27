from flask import make_response, jsonify, request
from maat_tracking.preset_model.PresetModel import PresetModel
from maat_tracking.audio_model.AudioModel import AudioModel
from maat_tracking.audio_model.AudioModelNoAdaptiveZoom import AudioModelNoAdaptiveZoom
from maat_tracking.object_model.model_one.QuickChangeObjectAudioModel import QuickChangeObjectAudio
from maat_tracking.object_model.model_two.WaitObjectAudioModel import WaitObjectAudioModel
from maat_tracking.updater import UpdateThread
from maat_tracking.object_model.yolov8 import YOLOPredict
from maat_web_app.integration import GeneralController, ModelCode


def start_thread_endpoint(integration: GeneralController):
    """ This method starts the thread that controls the actual tracking and calls
    the corresponding tracking model depending on the user's choice.
    """
    # start (unpause) the thread
    if (integration.thread is None) or (integration.event.value == 0):
        integration.event.value = 1
        if integration.tracking.value == ModelCode.PRESET:
            model = PresetModel(integration.cam_api, integration.mic_api,
                                filename=integration.filepath + "presets.json")
        elif integration.tracking.value == ModelCode.AUDIO:
            model = AudioModel(integration.cam_api, integration.mic_api,
                               filename=integration.filepath + "calibration.json")
        elif integration.tracking.value == ModelCode.AUDIONOZOOM:
            model = AudioModelNoAdaptiveZoom(integration.cam_api, integration.mic_api,
                                             filename=integration.filepath + "calibration.json")
        elif integration.tracking.value == ModelCode.HYBRID:
            model = QuickChangeObjectAudio(integration.cam_api, integration.mic_api,
                                           integration.nn, integration.footage_thread,
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
    """ Stops(pauses) the thread that controls the tracking
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


def is_running_endpoint(integration: GeneralController):
    """ Returns: Whether the thread that controls the tracking is currently running
    """
    return make_response(
        jsonify({"is-running": integration.thread and integration.thread.is_alive()}))


def track_presets(integration: GeneralController):
    """ Sets the current tracking model to PresetModel
    """
    integration.tracking.value = ModelCode.PRESET
    return make_response(jsonify({"tracking": integration.tracking.value}), 200)


def track_hybrid(integration: GeneralController):
    if integration.footage_thread_event.value == 0:
        return make_response(jsonify({"message": "Object tracking requires footage to be on. " +
                                                 "Please enable it before launching the program. " +
                                                 "To do this, make sure the NO_FOOTAGE environment " +
                                                 "variable is not set to \"true\"."}), 503)
    integration.tracking.value = ModelCode.HYBRID
    return make_response(jsonify({"tracking": integration.tracking.value}), 200)


def track_continuously(integration: GeneralController):
    """ Sets the current tracking model to the AudioModel
    """
    integration.tracking.value = ModelCode.AUDIO
    return make_response(jsonify({"tracking": integration.tracking.value}), 200)


def track_object_continuously(integration: GeneralController):
    """ Sets the current tracking model to ObjectModel
    """
    if integration.footage_thread_event.value == 0:
        return make_response(jsonify({"message": "Object tracking requires footage to be on. " +
                                                 "Please enable it before launching the program. " +
                                                 "To do this, make sure the NO_FOOTAGE environment " +
                                                 "variable is not set to \"true\"."}), 503)
    integration.tracking.value = ModelCode.OBJECT
    return make_response(jsonify({"tracking": integration.tracking.value}), 200)


def track_continuously_without_adaptive_zooming(integration: GeneralController):
    """ Sets the current tracking model to AudioModelNoAdaptiveZoom
    """
    integration.tracking.value = ModelCode.AUDIONOZOOM
    return make_response(jsonify({"tracking": integration.tracking.value}), 200)
