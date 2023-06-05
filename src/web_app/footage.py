from flask_socketio import emit
from web_app.integration import GeneralController
import base64


def emit_frame(integration: GeneralController):
    """ Sends the frame to the webpage via the web-socket
    Args:
        integration: The controller object
    """
    frame = integration.footage_thread.get_frame()
    emit("new-frame", {
        "base64": frame
    })
