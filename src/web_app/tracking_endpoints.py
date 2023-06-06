from flask import make_response, jsonify, request
from avonic_speaker_tracker.updater import UpdateThread
from web_app.integration import GeneralController

from web_app.integration import GeneralController, ModelCode
from avonic_camera_api.footage import ObjectTrackingThread
from object_tracker.yolov2 import YOLOPredict

def start_object_tracking_endpoint(integration: GeneralController):
    integration.preset = ModelCode.OBJECT_AUDIO
    if integration.nn is None:
        integration.nn = YOLOPredict()
    if integration.object_tracking_thread is None or integration.object_tracking_event.is_set():
        integration.object_tracking_thread = ObjectTrackingThread(integration.nn, integration.object_audio_model,
                                                                  integration.footage_thread, integration.object_tracking_event)
        integration.object_tracking_event.clear()
        integration.object_tracking_thread.start()
    else:
        return make_response(jsonify({}), 403)
    #integration.footage_thread.show_bounding_boxes = True
    return make_response(jsonify({}), 200)

def stop_object_tracking_endpoint(integration: GeneralController):
    # stop (pause) the object tracking thread
    integration.object_tracking_event.set()
    integration.object_tracking_thread.join()
    #integration.footage_thread.show_bounding_boxes = False
    return make_response(jsonify({}), 200)

def start_thread_endpoint(integration: GeneralController):
    # start (unpause) the thread
    if (integration.thread is None) or (integration.event.value == 0):
        if integration.thread is None:
            old_calibration = 0
        else:
            old_calibration = integration.thread.value
        integration.event.value = 1
        if integration.preset == ModelCode.PRESET:
            model = integration.preset_model
        elif integration.preset == ModelCode.AUDIO:
            model = integration.audio_model
        else:
            model = integration.object_audio_model
        integration.thread = UpdateThread(integration.event,
                                          integration.cam_api, integration.mic_api,
                                          model)
        integration.thread.set_calibration(old_calibration)

        integration.info_threads_event.value = 1
        integration.thread.start()
    else:
        print("Thread already running!")
        return make_response(jsonify({}), 403)
    return make_response(jsonify({}), 200)


def stop_thread_endpoint(integration: GeneralController):
    # stop (pause) the thread
    integration.event.value = 0
    integration.info_threads_event.value = 0
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
    print(integration.thread)
    print(integration.thread.is_alive())
    return make_response(
        jsonify({"is-running": integration.thread and integration.thread.is_alive()}))


#TO-DO: Change to enums for models
def preset_use(integration: GeneralController):
    if integration.preset.value == ModelCode.AUDIO:
        integration.preset.value = 0
    else:
        integration.preset.value = 1
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)
