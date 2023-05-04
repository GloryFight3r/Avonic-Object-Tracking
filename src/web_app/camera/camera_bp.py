from flask import Blueprint, render_template, request
from avonic_camera_api.zoom import Camera, CameraAPI

camera_bp = Blueprint('camera', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

'''
Another example with blueprints and templates.
See templates for interesting details.
'''
@camera_bp.route('/view')
def view():
    '''
    Dummy endpoint
    '''
    return "ok"

@camera_bp.post('/reboot')
def post_reboot():
    '''
    Endpoint triggers reboot procedure at the camera.
    '''
    # TODO add method from api that sends request to reboot camera
    return "ok"

@camera_bp.get('/get_zoom')
def get_zoom():
    """
    Endpoint to get the zoom value of the microphone.
    """
    api = CameraAPI(Camera())
    zoom = api.get_zoom()
    return str(zoom)

@camera_bp.post('/set_zoom')
def set_zoom():
    """
    Endpoint to set the zoom value of the microphone.
    """
    api = CameraAPI(Camera())
    value = int(request.get_json()["zoomValue"])
    api.direct_zoom(value)
    return "ok"
