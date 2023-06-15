from flask_socketio import emit
from web_app.integration import GeneralController



def emit_frame(integration: GeneralController):
    """ Sends the frame to the webpage via the web-socket
    Args:
        integration: The controller object
    """
    frame = integration.footage_thread.get_frame() # pragma: no mutate
    emit("new-frame", { # pragma: no mutate
        "base64": frame # pragma: no mutate
    })
