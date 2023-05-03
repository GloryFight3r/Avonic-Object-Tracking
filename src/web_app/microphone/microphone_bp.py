from flask import Blueprint, render_template, Response 
import json

from avonic_camera_api.converter import *
from microphone_api.stub_comms_microphone import *

microphone_bp = Blueprint('microphone', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

'''
When a post request is sent to /microphone/direction 
this method gets an angle from the microphone and 
returns a response containing the unit vector in that direction
'''
@microphone_bp.post('/direction')
def get_direction():
    azimuth = get_azimuth(30)
    elevation = get_elevation(30)

    vec = angle_vector(np.deg2rad(azimuth),np.deg2rad(elevation))
    msg = json.dumps(vec.tolist())
    print(msg)
    return Response(msg,status = 200)
