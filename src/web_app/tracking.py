from threading import Event
from flask import make_response, jsonify


def start_thread_endpoint(event: Event):
    # start (unpause) the thread
    print("Started thread")
    event.set()
    return make_response(jsonify({}), 200)


def stop_thread_endpoint(event: Event):
    # start (unpause) the thread
    print("Stopping thread")
    event.clear()
    return make_response(jsonify({}), 200)
