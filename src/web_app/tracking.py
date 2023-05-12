from flask import make_response, jsonify, request
from avonic_speaker_tracker.custom_thread import CustomThread
from web_app.integration import GeneralController


def start_thread_endpoint(integration: GeneralController):
    # start (unpause) the thread
    print("Started thread")
    if integration.thread is None:
        integration.thread = CustomThread(integration.event, integration.url, integration.cam_api, integration.mic_api)
        integration.thread.set_calibration(2)
        integration.event.clear()
        integration.thread.start()
    else:
        old_calibration = integration.thread.value
        integration.thread = CustomThread(integration.event, integration.url, integration.cam_api, integration.mic_api)
        integration.thread.set_calibration(old_calibration)
        integration.event.clear()
        integration.thread.start()
    return make_response(jsonify({}), 200)


def stop_thread_endpoint(integration: GeneralController):
    # stop (pause) the thread
    print("Stopping thread")
    integration.event.set()
    integration.thread.join()
    return make_response(jsonify({}), 200)


def update_microphone(integration: GeneralController):
    data = request.get_json()
    integration.ws.emit('microphone-update', data)
    return make_response(jsonify({}), 200)
