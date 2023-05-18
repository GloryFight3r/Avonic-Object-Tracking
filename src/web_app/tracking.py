from flask import make_response, jsonify, request
from avonic_speaker_tracker.custom_thread import CustomThread
from web_app.integration import GeneralController
from avonic_speaker_tracker.preset_control import find_most_similar_preset
import numpy as np


def start_thread_endpoint(integration: GeneralController):
    # start (unpause) the thread
    print("Started thread")
    if integration.thread is None:
        integration.thread = CustomThread(integration.event, integration.url,
                                          integration.cam_api, integration.mic_api)
        integration.thread.set_calibration(2)
        integration.event.clear()
        integration.thread.start()
    else:
        old_calibration = integration.thread.value
        integration.thread = CustomThread(integration.event, integration.url,
                                          integration.cam_api, integration.mic_api)
        integration.thread.set_calibration(old_calibration)
        integration.event.clear()
        integration.thread.start()
    return make_response(jsonify({}), 200)

def point(integration: GeneralController):
    preset_names = np.array(integration.preset_locations.get_preset_list())
    presets_mic = []
    for i in range(len(preset_names)):
        presets_mic.append(integration.preset_locations.get_preset_info(preset_names[i])[1])
    mic_direction = integration.mic_api.get_direction()
    id = find_most_similar_preset(mic_direction,presets_mic)
    preset = integration.preset_locations.get_preset_info(preset_names[id])
    print("fine")
    integration.cam_api.move_absolute(15, 15,
                          int(preset[0][0]), int(preset[0][1]))
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

def is_running_endpoint(integration: GeneralController):
    return make_response(jsonify({"is-running": integration.thread and integration.thread.is_alive()}))
