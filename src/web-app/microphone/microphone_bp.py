from flask import Blueprint, render_template, Response 
import json 

from microphone_api.stub_comms_microphone import *
from avonic_camera_api.converter import *

microphone_bp = Blueprint('microphone', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

'''
When a post request is sent to /microphone/direction 
this method gets the angle from the microphone and 
returns a response containing the unit vector in that direction
'''
@microphone_bp.post('/direction')
def get_direction():
    azimuth = get_azimuth(45)
    elevation = get_elevation(90)

    vec = angle_vector(azimuth,elevation)
    msg = json.dumps(vec.tolist())
    print(msg)
    return Response(msg,status = 200)
