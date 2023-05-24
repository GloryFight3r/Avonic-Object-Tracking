from flask import Flask, jsonify, abort, render_template, make_response, Response
from flask_socketio import SocketIO
import web_app.camera_endpoints
import web_app.microphone_endpoints
import web_app.preset_locations_endpoints
import web_app.general_endpoints
import web_app.tracking
import web_app.footage
from web_app.integration import GeneralController

integration = GeneralController()


def create_app(test_controller=None):
    # create and configure the app
    app = Flask(__name__)

    if test_controller is None:
        integration.load_env()
        app.config['SECRET_KEY'] = integration.secret
    else:
        integration.copy(test_controller)
        app.config['SECRET_KEY'] = 'test'

    integration.ws = SocketIO(app)

    @app.get('/fail-me')
    def fail_me():
        abort(418)

    @app.get('/')
    def view():
        return render_template('view.html')

    @app.get('/camera_control')
    def camera_view():
        return render_template('camera.html')

    @app.get('/microphone_control')
    def microphone_view():
        return render_template('microphone.html')

    @app.get('/presets_and_calibration')
    def presets_and_calibration_view():
        return render_template('presets_and_calibration.html')

    @app.get('/live_footage')
    def live_footage_view():
        return render_template('live_footage.html')

    @app.post('/camera/reboot')
    def post_reboot():
        """
        Endpoint triggers reboot procedure at the camera.
        """
        return web_app.camera_endpoints.reboot_camera_endpoint(integration)

    @app.post('/camera/on')
    def post_turn_on_camera():
        """
        Endpoint triggers turn on procedure at the camera.
        """
        return web_app.camera_endpoints.turn_on_camera_endpoint(integration)

    @app.post('/camera/off')
    def post_off():
        """
        Endpoint triggers turn off at the camera.
        """
        return web_app.camera_endpoints.turn_off_camera_endpoint(integration)

    @app.post('/camera/move/absolute')
    def post_move_absolute():
        return web_app.camera_endpoints.move_absolute_camera_endpoint(integration)

    @app.post('/camera/move/relative')
    def post_move_relative():
        return web_app.camera_endpoints.move_relative_camera_endpoint(integration)

    @app.post('/camera/move/vector')
    def post_move_vector():
        return web_app.camera_endpoints.move_vector_camera_endpoint(integration)

    @app.post('/camera/move/home')
    def post_home():
        return web_app.camera_endpoints.move_home_camera_endpoint(integration)

    @app.post('/camera/move/stop')
    def stop():
        """
        Endpoint to stop the rotation of the camera.
        """
        return web_app.camera_endpoints.move_stop_camera_endpoint(integration)

    @app.get('/camera/zoom/get')
    def get_zoom():
        """
        Endpoint to get the zoom value of the camera.
        """
        return web_app.camera_endpoints.zoom_get_camera_endpoint(integration)

    @app.post('/camera/zoom/set')
    def set_zoom():
        """
        Endpoint to set the zoom value of the camera.
        """
        return web_app.camera_endpoints.zoom_set_camera_endpoint(integration)

    @app.get('/camera/position/get')
    def get_position():
        """
        Endpoint to get the position value of the camera.
        """
        return web_app.camera_endpoints.position_get_camera_endpoint(integration)

    @app.post('/microphone/height/set')
    def set_height():
        """
        Endpoint to set the height of the microphone.
        """
        return web_app.microphone_endpoints.height_set_microphone_endpoint(integration)

    @app.get('/microphone/direction')
    def get_direction():
        """
        Endpoint to get the direction of the last speaker.
        """
        return web_app.microphone_endpoints.direction_get_microphone_endpoint(integration)

    @app.get('/microphone/speaker/direction')
    def get_speaker_direction():
        """
        Endpoint to get the direction of the active speaker.
        """
        return web_app.microphone_endpoints.get_speaker_direction_endpoint(integration)

    @app.get('/microphone/speaking')
    def get_speaking():
        """
        Endpoint to inquire whether anyone is speaking.
        """
        return web_app.microphone_endpoints.speaking_get_microphone_endpoint(integration)

    @app.get('/calibration/add_directions_to_speaker')
    def add_calibration_speaker():
        return web_app.general_endpoints.add_calibration_speaker(integration)

    @app.get('/calibration/add_direction_to_mic')
    def add_calibration_mic():
        return web_app.general_endpoints.add_calibration_to_mic(integration)

    @app.get('/calibration/reset')
    def reset_calibration():
        return web_app.general_endpoints.reset_calibration(integration)

    @app.post('/preset/add')
    def add_preset():
        return web_app.preset_locations_endpoints.add_preset_location(integration)

    @app.post('/preset/edit')
    def edit_preset():
        return web_app.preset_locations_endpoints.edit_preset_location(integration)

    @app.post('/preset/remove')
    def remove_preset():
        return web_app.preset_locations_endpoints.remove_preset_location(integration)

    @app.get('/preset/get_list')
    def get_preset_list():
        return web_app.preset_locations_endpoints.get_preset_list(integration)

    @app.post('/preset/get_preset_info')
    def get_preset_info():
        return web_app.preset_locations_endpoints.get_preset_info(integration)

    @app.get('/preset/point')
    def point_to_preset():
        return web_app.preset_locations_endpoints.point_to_closest_preset(integration)

    @app.get('/calibration/is_set')
    def calibration_is_set():
        return web_app.general_endpoints.is_calibrated(integration)

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

    @app.post('/thread/start')
    def thread_start():
        return web_app.tracking.start_thread_endpoint(integration)

    @app.post('/thread/stop')
    def thread_stop():
        return web_app.tracking.stop_thread_endpoint(integration)

    @app.get('/thread/running')
    def thread_is_running():
        # checks whether thread is running
        return web_app.tracking.is_running_endpoint(integration)

    @app.get('/thread/value')
    def thread_value():
        # Retrieves the thread value (only for demo/debug purposes)
        if integration.thread is None:
            return make_response(jsonify({"value": "NONE"}), 200)
        print(integration.thread.value)
        return make_response(jsonify({"value": integration.thread.value}), 200)

    @app.post('/update/microphone')
    def thread_microphone():
        return web_app.tracking.update_microphone(integration)

    @app.post('/update/camera')
    def thread_camera():
        return web_app.tracking.update_camera(integration)

    @integration.ws.on("request-frame")
    def camera_frame_requested(message):
        web_app.footage.emit_frame(integration)

#    # Camera footage
#    @app.route('/video_feed')
#    def video_feed():
#        return Response(web_app.camera_endpoints.get_camera_footage(integration), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app


application = create_app()
