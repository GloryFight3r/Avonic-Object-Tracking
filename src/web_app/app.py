
from flask import Flask, session, jsonify, current_app, abort, render_template, make_response, request, Response
import socket
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_adapter import Camera
from microphone_api.stub_comms_microphone import *
from avonic_camera_api.converter import *
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = ('192.168.5.94', 1259)
api = CameraAPI(None)

app = Flask(__name__)

def success():
    return make_response(jsonify({}), 200)

@app.get('/fail-me')
def fail_me():
    abort(418)

@app.get('/')
def view():
    return render_template('view.html')

@app.post('/camera/reboot')
def post_reboot():
    '''
    Endpoint triggers reboot procedure at the camera.
    '''
    api.reboot()
    return success()

@app.post('/camera/on')
def post_on():
    '''
    Endpoint triggers turn on procedure at the camera.
    '''
    api.turn_on()
    return success()

@app.post('/camera/off')
def post_off():
    '''
    Endpoint triggers turn off at the camera.
    '''
    api.turn_off()
    return success()

@app.post('/camera/move/absolute')
def post_move_absolute():
    data = request.get_json()
    print(data)
    api.move_absolute(int(data["absolute-speed-x"]), int(data["absolute-speed-y"]), int(data["absolute-degrees-x"]), int(data["absolute-degrees-y"]))
    return success()

@app.post('/camera/move/relative')
def post_move_relative():
    data = request.get_json()
    api.move_relative(int(data["relative-speed-x"]), int(data["relative-speed-y"]), int(data["relative-degrees-x"]), int(data["relative-degrees-y"]))
    return success()

@app.post('/camera/move/home')
def post_home():
    api.home()
    return success()

@app.get('/camera/zoom/get')
def get_zoom():
    """
    Endpoint to get the zoom value of the camera.
    """
    zoom = api.get_zoom()
    print(zoom)
    return str(zoom)

@app.post('/camera/zoom/set')
def set_zoom():
    """
    Endpoint to set the zoom value of the camera.
    """
    value = int(request.get_json()["zoomValue"])
    api.direct_zoom(value)
    return success()

@app.post('/camera/move/stop')
def stop():
    """
    Endpoint to stop the rotation of the camera.
    """
    api.stop()
    return success()


@app.post('/microphone/direction')
def get_direction():
    '''
    When a post request is sent to /microphone/direction 
    this method gets an angle from the microphone and 
    :returns: a response containing the unit vector in that direction
    '''
    api = MicrophoneAPI()
    azimuth = api.get_azimuth(30)
    elevation = api.get_elevation(30)

    vec = angle_vector(np.deg2rad(azimuth),np.deg2rad(elevation))
    msg = json.dumps(vec.tolist())
    print(msg)
    return Response(msg,status = 200)