from flask import Flask, jsonify, abort, render_template, make_response, request, Response
import socket
import json
from dotenv import load_dotenv
from os import getenv
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_adapter import Camera
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import UDPSocket

load_dotenv()
cam_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cam_addr = (getenv("CAM_IP"), int(getenv("CAM_PORT")))
cam_api = CameraAPI(Camera(cam_sock, cam_addr))
mic_addr = (getenv("MIC_IP"), int(getenv("MIC_PORT")))
mic_api = MicrophoneAPI(UDPSocket(mic_addr), int(getenv("MIC_THRESH")))

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
    """
    Endpoint triggers reboot procedure at the camera.
    """
    cam_api.reboot()
    return success()


@app.post('/camera/on')
def post_on():
    """
    Endpoint triggers turn on procedure at the camera.
    """
    cam_api.turn_on()
    return success()


@app.post('/camera/off')
def post_off():
    """
    Endpoint triggers turn off at the camera.
    """
    cam_api.turn_off()
    return success()


@app.post('/camera/move/absolute')
def post_move_absolute():
    data = request.get_json()
    cam_api.move_absolute(int(data["absolute-speed-x"]), int(data["absolute-speed-y"]),
                          int(data["absolute-degrees-x"]), int(data["absolute-degrees-y"]))
    return success()


@app.post('/camera/move/relative')
def post_move_relative():
    data = request.get_json()
    cam_api.move_relative(int(data["relative-speed-x"]), int(data["relative-speed-y"]),
                          int(data["relative-degrees-x"]), int(data["relative-degrees-y"]))
    return success()


@app.post('/camera/move/vector')
def post_move_vector():
    value = request.get_json()
    cam_api.move_vector(int(value["vector-speed-x"]), int(value["vector-speed-y"]),
                        [float(value["vector-x"]), float(value["vector-y"]),
                         float(value["vector-z"])])
    return success()


@app.post('/camera/move/home')
def post_home():
    cam_api.home()
    return success()


@app.get('/camera/zoom/get')
def get_zoom():
    """
    Endpoint to get the zoom value of the camera.
    """
    zoom = cam_api.get_zoom()
    return str(zoom)


@app.post('/camera/zoom/set')
def set_zoom():
    """
    Endpoint to set the zoom value of the camera.
    """
    value = int(request.get_json()["zoomValue"])
    cam_api.direct_zoom(value)
    return success()


@app.post('/camera/move/stop')
def stop():
    """
    Endpoint to stop the rotation of the camera.
    """
    cam_api.stop()
    return success()

@app.post('/microphone/height/set')
def set_height():
    """
    Endpoint to set the height of the microphone.
    """
    mic_api.set_height(float(request.get_json()["microphoneHeight"]))
    return str(mic_api.height)

@app.get('/microphone/direction')
def get_direction():
    """
    Endpoint to get the direction of the speaker.
    """
    msg = json.dumps(list(mic_api.get_direction()))
    return Response(msg, status=200)


@app.get('/microphone/speaking')
def get_speaking():
    """
    Endpoint to inquire whether anyone is speaking.
    """
    return Response(json.dumps(mic_api.is_speaking()), status=200)
