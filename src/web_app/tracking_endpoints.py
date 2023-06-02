from flask import make_response, jsonify, request
from avonic_speaker_tracker.updater import UpdateThread
from web_app.integration import GeneralController
from avonic_camera_api.footage import ObjectTrackingThread

def start_object_tracking_endpoint(integration: GeneralController):
    if integration.object_tracking_thread is None or integration.object_tracking_event.is_set():
        integration.object_tracking_thread = ObjectTrackingThread(integration.nn, integration.calibration_tracker,
                                                                  integration.footage_thread, integration.object_tracking_event)
        integration.object_tracking_event.clear()
        integration.object_tracking_thread.start()
    else:
        return make_response(jsonify({}), 403)
    integration.footage_thread.show_bounding_boxes = True
    return make_response(jsonify({}), 200)

def stop_object_tracking_endpoint(integration: GeneralController):
    # stop (pause) the object tracking thread
    integration.object_tracking_event.set()
    integration.object_tracking_thread.join()
    integration.footage_thread.show_bounding_boxes = False
    return make_response(jsonify({}), 200)


def start_thread_endpoint(integration: GeneralController, allow_movement):
    # start (unpause) the thread
    if integration.thread is None:
        # FIXME: UGLY code repetition please fix
        integration.thread = UpdateThread(integration.event, integration.url,
                                          integration.cam_api, integration.mic_api,
                                          integration.preset_locations, integration.calibration,
                                          integration.preset, integration.calibration_tracker,
                                          allow_movement)
        integration.thread.set_calibration(2)
        integration.event.clear()
        integration.thread.start()
    elif integration.event.is_set():
        old_calibration = integration.thread.value
        integration.thread = UpdateThread(integration.event, integration.url,
                                          integration.cam_api, integration.mic_api,
                                          integration.preset_locations, integration.calibration,
                                          integration.preset, integration.calibration_tracker,
                                          allow_movement)
        integration.thread.set_calibration(old_calibration)
        integration.event.clear()
        integration.thread.start()
    else:
        print("Thread already running!")
        return make_response(jsonify({}), 403)
    return make_response(jsonify({}), 200)


def stop_thread_endpoint(integration: GeneralController):
    # stop (pause) the thread
    integration.event.set()
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


def preset_use(integration: GeneralController):
    integration.preset = not integration.preset
    print(integration.preset)
    return make_response(jsonify({"preset":integration.preset}), 200)
