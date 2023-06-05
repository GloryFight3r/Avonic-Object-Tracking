from flask import make_response, jsonify, request
from avonic_speaker_tracker.updater import UpdateThread
from web_app.integration import GeneralController


def start_thread_endpoint(integration: GeneralController):
    # start (unpause) the thread
    if (integration.thread is None) or (integration.event.value == 0):
        if integration.thread is None:
            old_calibration = 0
        else:
            old_calibration = integration.thread.value
        integration.event.value = 1
        integration.thread = UpdateThread(integration.event,
                                          integration.cam_api, integration.mic_api,
                                          integration.preset)
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

def track_presets(integration: GeneralController):
    integration.preset.value = 1
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def track_continuously(integration: GeneralController):
    integration.preset.value = 0
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)

def preset_use(integration: GeneralController):
    if integration.preset.value == 1:
        integration.preset.value = 0
    else:
        integration.preset.value = 1
    print(integration.preset.value)
    return make_response(jsonify({"preset":integration.preset.value}), 200)
