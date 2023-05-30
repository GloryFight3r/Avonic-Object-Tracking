from flask import Flask, jsonify, abort, render_template, make_response, Response, request
from flask_socketio import SocketIO
import web_app.camera_endpoints
import web_app.microphone_endpoints
import web_app.preset_locations_endpoints
import web_app.footage
import web_app.calibration_endpoints
import web_app.tracking_endpoints
import web_app.footage
from web_app.integration import GeneralController

# While testing to keep the log clean
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

integration = GeneralController()

def create_app(test_controller=None):
    # create and configure the app
    app = Flask(__name__)

    if test_controller is None:
        integration.load_env()
        app.config['SECRET_KEY'] = integration.secret
        integration.ws = SocketIO(app)
    else:
        integration.copy(test_controller)
        app.config['SECRET_KEY'] = 'test'

    @app.get('/fail-me')
    def fail_me():
        abort(418)

    @app.get('/')
    def view():
        to_import=["camera", "microphone", "presets", "calibration",
                   "footage", "thread", "scene", "socket", "main"]
        return render_template('view.html', to_import=to_import, page_name="Main page")

    @app.get('/camera_control')
    def camera_view():
        to_import=["camera", "socket", "main"]
        return render_template('single_page.html', name="camera", to_import=to_import, 
                               page_name="Camera View")
    @app.get('/microphone_control')
    def microphone_view():
        to_import=["microphone", "socket", "main"]
        return render_template('single_page.html', name="microphone", to_import=to_import,
                               page_name="Microphone View")

    @app.get('/presets_and_calibration')
    def presets_and_calibration_view():
        to_import=["socket", "presets", "calibration", "main"]
        return render_template('single_page.html', name="presets_and_calibration", to_import=to_import,
                               page_name="Presets & Calibration View")

    @app.get('/live_footage')
    def live_footage_view():
        to_import=["footage", "socket", "main"]
        return render_template('single_page.html', name="live_footage", to_import=to_import,
                               page_name="Live Footage")

    @app.get('/thread')
    def thread_view():
        to_import=["thread", "socket", "main"]
        return render_template('single_page.html', name="thread", to_import=to_import,
                               page_name="Thread view")

    @app.get('/visualisation')
    def visualisation_view():
        to_import=["scene", "socket"]
        return render_template('single_page.html', name="visualisation", to_import=to_import,
                               page_name="Visualisation view")

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

    @app.get('/preset/info/<preset_name>')
    def get_preset_info(preset_name):
        return web_app.preset_locations_endpoints.get_preset_info(integration, preset_name)

    @app.post('/preset/point')
    def point_to_preset():
        return web_app.preset_locations_endpoints.point_to_closest_preset(integration)

    @app.get('/calibration/add_directions_to_speaker')
    def add_calibration_speaker():
        return web_app.calibration_endpoints.add_calibration_speaker(integration)

    @app.get('/calibration/add_direction_to_mic')
    def add_calibration_mic():
        return web_app.calibration_endpoints.add_calibration_to_mic(integration)

    @app.get('/calibration/reset')
    def reset_calibration():
        return web_app.calibration_endpoints.reset_calibration(integration)

    @app.get('/calibration/is_set')
    def calibration_is_set():
        return web_app.calibration_endpoints.is_calibrated(integration)

    @app.get('/calibration/camera')
    def calibration_get_cam_coords():
        return web_app.calibration_endpoints.get_calibration(integration)

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
        return web_app.tracking_endpoints.start_thread_endpoint(integration)

    @app.post('/thread/stop')
    def thread_stop():
        return web_app.tracking_endpoints.stop_thread_endpoint(integration)

    @app.get('/thread/running')
    def thread_is_running():
        # checks whether thread is running
        return web_app.tracking_endpoints.is_running_endpoint(integration)

    @app.get('/thread/value')
    def thread_value():
        # Retrieves the thread value (only for demo/debug purposes)
        if integration.thread is None:
            return make_response(jsonify({"value": "NONE"}), 200)
        print(integration.thread.value)
        return make_response(jsonify({"value": integration.thread.value}), 200)

    @app.post('/update/microphone')
    def thread_microphone():
        return web_app.tracking_endpoints.update_microphone(integration)

    @app.post('/update/camera')
    def thread_camera():
        return web_app.tracking_endpoints.update_camera(integration)

    @integration.ws.on("request-frame")
    def camera_frame_requested(message):
        web_app.footage.emit_frame(integration)

    @app.post('/update/calibration')
    def thread_calibration():
        return web_app.tracking_endpoints.update_calibration(integration)
#    # Camera footage
#    @app.route('/video_feed')
#    def video_feed():
#        return Response(web_app.camera_endpoints.get_camera_footage(integration), mimetype='multipart/x-mixed-replace; boundary=frame')

    return app

if __name__ == "__main__":
    application = create_app()
