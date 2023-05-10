from threading import Event
from os import getenv
import socket
from dotenv import load_dotenv
from flask import Flask, jsonify, abort, render_template, make_response

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_adapter import Camera
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import UDPSocket
import web_app.camera_endpoints
import web_app.microphone_endpoints
import web_app.tracking

load_dotenv()
cam_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cam_addr = (getenv("CAM_IP"), int(getenv("CAM_PORT")))
cam_api = CameraAPI(Camera(cam_sock, cam_addr))
mic_addr = (getenv("MIC_IP"), int(getenv("MIC_PORT")))
mic_sock = UDPSocket(mic_addr)
mic_api = MicrophoneAPI(mic_sock, int(getenv("MIC_THRESH")))

event = Event()
thread = [ None ] 

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

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
        return web_app.camera_endpoints.reboot_camera_endpoint(cam_api)


    @app.post('/camera/on')
    def post_turn_on_camera():
        """
        Endpoint triggers turn on procedure at the camera.
        """
        return web_app.camera_endpoints.turn_on_camera_endpoint(cam_api)


    @app.post('/camera/off')
    def post_off():
        """
        Endpoint triggers turn off at the camera.
        """
        return web_app.camera_endpoints.turn_off_camera_endpoint(cam_api)


    @app.post('/camera/move/absolute')
    def post_move_absolute():
        return web_app.camera_endpoints.move_absolute_camera_endpoint(cam_api)


    @app.post('/camera/move/relative')
    def post_move_relative():
        return web_app.camera_endpoints.move_relative_camera_endpoint(cam_api)


    @app.post('/camera/move/vector')
    def post_move_vector():
        return web_app.camera_endpoints.move_vector_camera_endpoint(cam_api)


    @app.post('/camera/move/home')
    def post_home():
        return web_app.camera_endpoints.move_home_camera_endpoint(cam_api)


    @app.post('/camera/move/stop')
    def stop():
        """
        Endpoint to stop the rotation of the camera.
        """
        return web_app.camera_endpoints.move_stop_camera_endpoint(cam_api)


    @app.get('/camera/zoom/get')
    def get_zoom():
        """
        Endpoint to get the zoom value of the camera.
        """
        return web_app.camera_endpoints.zoom_get_camera_endpoint(cam_api)


    @app.post('/camera/zoom/set')
    def set_zoom():
        """
        Endpoint to set the zoom value of the camera.
        """
        return web_app.camera_endpoints.zoom_set_camera_endpoint(cam_api)


    @app.post('/microphone/height/set')
    def set_height():
        """
        Endpoint to set the height of the microphone.
        """
        return web_app.microphone_endpoints.height_set_microphone_endpoint(mic_api)


    @app.get('/microphone/direction')
    def get_direction():
        """
        Endpoint to get the direction of the speaker.
        """
        return web_app.microphone_endpoints.direction_get_microphone_endpoint(mic_api)


    @app.get('/microphone/speaking')
    def get_speaking():
        """
        Endpoint to inquire whether anyone is speaking.
        """
        return web_app.microphone_endpoints.speaking_get_microphone_endpoint(mic_api)

    # THIS IS FOR DEMO PURPOSES ONLY
    # SHOULD BE CHANGED WHEN BASIC PRESET FUNCTIONALITY ADDED

    # This part of app is responsible for running a thread for tracking.
    # # Please refer to wiki, if needed.

    # event - acts as a flag for the created thread.
    # When false (cleared) - the execution of thread is locked
    # When true (set) - the execution of the thread is allowed
    # Set to false by default. Respective endpoints set/clear it.

    # <CustomThread> (should pick a better name) contains all code for the actual tracking.
    # Use set calibration to set the calibration parameters that are going to be used when tracking

    # The thread is started at the start of the program to avoid
    # python's "global" identifier and because threads can't be paused

    # create the event and start the thread

    @app.get('/thread/start')
    def thread_start():
        return web_app.tracking.start_thread_endpoint(event, thread)


    @app.get('/thread/stop')
    def thread_stop():
        return web_app.tracking.stop_thread_endpoint(event, thread)


    @app.get('/thread/value')
    def thread_value():
        # Retrieves the thread value (only for demo/debug purposes)
        if thread[0] is None:
            return make_response(jsonify({"value" : "NONE"}), 200)
        print(thread[0].value)
        return make_response(jsonify({"value" : thread[0].value}), 200)

    return app