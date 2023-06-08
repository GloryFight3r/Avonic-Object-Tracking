from flask import make_response, jsonify, request
import numpy as np
from avonic_speaker_tracker.updater import UpdateThread
from web_app.integration import GeneralController

from web_app.integration import GeneralController, ModelCode
from avonic_camera_api.footage import ObjectTrackingThread
from object_tracker.yolov2 import YOLOPredict
from avonic_speaker_tracker.object_model.ObjectModel import WaitObjectAudioModel


#def stop_object_tracking_endpoint(integration: GeneralController):
#    # stop (pause) the object tracking thread
#    integration.object_tracking_event.set()
#    integration.object_tracking_thread.join()
#    #integration.footage_thread.show_bounding_boxes = False
#    return make_response(jsonify({}), 200)

def start_thread_endpoint(integration: GeneralController):
    # start (unpause) the thread
    if (integration.thread is None) or (integration.event.value == 0):
        if integration.thread is None:
            old_calibration = 0
        else:
            old_calibration = integration.thread.value
        integration.event.value = 1
        print("VALUE")
        print(integration.preset.value)
        if integration.preset.value == ModelCode.PRESET:
            model = integration.preset_model
        elif integration.preset.value == ModelCode.AUDIO:
            model = integration.audio_model
        else:
            if integration.nn is None:
                integration.nn = YOLOPredict()
            integration.object_tracking_thread = \
                ObjectTrackingThread(integration.nn, integration.object_audio_model,
                    integration.footage_thread, integration.object_tracking_event)
            integration.object_tracking_event.value = 1
            integration.object_tracking_thread.start()

            integration.object_audio_model = WaitObjectAudioModel(
                    integration.cam_api, integration.mic_api, integration.object_tracking_thread,
                    np.array([1920.0, 1080.0]),
                    5, filename="calibration.json")
            model = integration.object_audio_model

        print(model)

        integration.thread = UpdateThread(integration.event,
                                          integration.cam_api, integration.mic_api,
                                          model)
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
    integration.object_tracking_event.value = 0

    if integration.object_tracking_thread is not None:
        integration.object_tracking_thread.join()
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

def track_presets(integration: GeneralController):
    integration.preset.value = ModelCode.PRESET
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_continuously(integration: GeneralController):
    integration.preset.value = ModelCode.AUDIO
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_object_continuously(integration: GeneralController):
    integration.preset.value = ModelCode.OBJECT_AUDIO
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)

#TO-DO: Change to enums for models
def preset_use(integration: GeneralController):
    pass
#    if integration.preset.value == ModelCode.AUDIO:
#        integration.preset.value = ModelCode.PRESET
#    else:
#        integration.preset.value = ModelCode.AUDIO
#    print(integration.preset.value)
#    return make_response(jsonify({"preset":integration.preset.value}), 200)
