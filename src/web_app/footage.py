from flask import make_response, jsonify, request
from flask_socketio import emit
from web_app.integration import GeneralController
import base64

def update_footage(integration: GeneralController):
    data = request.get_json()
    integration.ws.emit('footage-update', data)
    return make_response(jsonify({}), 200) 

def emit_frame(integration: GeneralController):
    frame = integration.footage_thread.get_frame()
    emit("new-frame", {
        "base64": frame
    })
