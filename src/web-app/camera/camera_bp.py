from flask import Blueprint, render_template
from avonic_camera_api.zoom import Camera, API

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
    '''
    Endpoint triggers reboot procedure at the camera.
    '''
    api = API(Camera())
    return str(api.get_zoom())

@camera_bp.post('/set_zoom')
def set_zoom():
    '''
    Endpoint triggers reboot procedure at the camera.
    '''
    api = API(Camera())
    value = 100
    return str(api.direct_zoom(value))
