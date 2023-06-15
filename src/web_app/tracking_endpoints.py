from flask import make_response, jsonify, request
from avonic_speaker_tracker.updater import UpdateThread
from web_app.integration import GeneralController, ModelCode
from avonic_speaker_tracker.object_model.yolov8 import YOLOPredict

def start_thread_endpoint(integration: GeneralController):
    # start (unpause) the thread
    if (integration.thread is None) or (integration.event.value == 0):
        if integration.thread is None:
            old_calibration = 0
        else:
            old_calibration = integration.thread.value
        integration.event.value = 1
        if integration.preset.value == ModelCode.PRESET:
            model = integration.preset_model
        elif integration.preset.value == ModelCode.AUDIO:
            model = integration.audio_model
        elif integration.preset.value == ModelCode.AUDIONOZOOM:
            model = integration.audio_no_zoom_model
        else:
            if integration.nn is None:
                integration.nn = YOLOPredict()
                integration.object_audio_model.nn = integration.nn

            model = integration.object_audio_model

        integration.thread = UpdateThread(integration.event,
                                          integration.cam_api, integration.mic_api,
                                          model, integration.filepath)
        integration.event.value = 1
        integration.thread.set_calibration(old_calibration)

        integration.info_threads_event.value = 1
        integration.thread.start()
        return make_response(jsonify({}), 200)
    else:
        print("Thread already running!")
        return make_response(jsonify({}), 403)


def stop_thread_endpoint(integration: GeneralController):
    # stop (pause) the thread
    integration.event.value = 0
    integration.info_threads_event.value = 0

    if integration.thread is not None:
        integration.thread.join()
    return make_response(jsonify({}), 200)


def update_microphone(integration: GeneralController):
    data = request.get_json()
    integration.ws.emit('microphone-update', data)
    return make_response(jsonify({}), 200)


def update_camera(integration: GeneralController):
    data = request.get_json()
    integration.ws.emit('camera-update', data)
    return make_response(jsonify({}), 200)


def update_calibration(integration: GeneralController):
    data = request.get_json()
    integration.ws.emit('calibration-update', data)
    return make_response(jsonify({}), 200)


def is_running_endpoint(integration: GeneralController):
    return make_response(
        jsonify({"is-running": integration.thread and integration.thread.is_alive()}))

def track_presets(integration: GeneralController):
    integration.preset.value = ModelCode.PRESET
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_continuously(integration: GeneralController):
    integration.preset.value = ModelCode.AUDIO
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_object_continuously(integration: GeneralController):
    integration.preset.value = ModelCode.OBJECT
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_continuously_without_adaptive_zooming(integration: GeneralController):
    integration.preset.value = ModelCode.AUDIONOZOOM
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def preset_use(integration: GeneralController):
    if integration.preset.value == 1:
        integration.preset.value = 0
    else:
        integration.preset.value = 1
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)
