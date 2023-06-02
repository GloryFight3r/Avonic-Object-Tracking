from flask import make_response, jsonify, request
from avonic_speaker_tracker.updater import UpdateThread
from web_app.integration import GeneralController


def start_thread_endpoint(integration: GeneralController):
    # start (unpause) the thread
    if (integration.thread is None) or (integration.event.is_set()):
        if integration.thread is None:
            old_calibration = 0
        else:
            old_calibration = integration.thread.value
        integration.thread = UpdateThread(integration.event, integration.url,
                                          integration.cam_api, integration.mic_api,
                                          integration.get_model_based_on_choice())
        integration.thread.set_calibration(old_calibration)
        integration.event.clear()
        integration.info_threads_event.clear()
        integration.thread.start()
    else:
        print("Thread already running!")
        return make_response(jsonify({}), 403)
    return make_response(jsonify({}), 200)


def stop_thread_endpoint(integration: GeneralController):
    # stop (pause) the thread
    integration.event.set()
    integration.info_threads_event.set()
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


def preset_use(integration: GeneralController):
    integration.preset = not integration.preset
    print(integration.preset)
    return make_response(jsonify({"preset":integration.preset}), 200)
