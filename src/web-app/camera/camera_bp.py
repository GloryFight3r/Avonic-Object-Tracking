from flask import Blueprint, render_template

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
