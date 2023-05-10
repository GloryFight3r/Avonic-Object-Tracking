from threading import Event
from flask import make_response, jsonify
from avonic_speaker_tracker.custom_thread import CustomThread


def start_thread_endpoint(event: Event, thread):
    # start (unpause) the thread
    print("Started thread")
    if thread[0] is None:
        thread[0] = CustomThread(event)
        thread[0].set_calibration(2)
        event.clear()
        thread[0].start()
    else:
        old_calibration = thread[0].value
        thread[0] = CustomThread(event)
        thread[0].set_calibration(old_calibration)
        event.clear()
        thread[0].start()
    return make_response(jsonify({}), 200)


def stop_thread_endpoint(event: Event, thread):
    # start (unpause) the thread
    print("Stopping thread")
    event.set()
    thread[0].join()
    return make_response(jsonify({}), 200)
