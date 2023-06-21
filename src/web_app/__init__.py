import signal
import logging
from flask import Flask, jsonify, abort, render_template, make_response
from flask_socketio import SocketIO
import web_app.camera_endpoints
import web_app.microphone_endpoints
import web_app.preset_locations_endpoints
import web_app.footage
import web_app.calibration_endpoints
import web_app.tracking_endpoints
import web_app.footage
import web_app.settings_endpoints
from web_app.integration import GeneralController, close_running_threads

# While testing to keep the log clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
#import logging
#log = logging.getLogger('werkzeug')
#log.setLevel(logging.ERROR)

integration = GeneralController()

restart_queue = None

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
        integration.testing.value = 1

    @app.get('/fail-me')
    def fail_me():
        abort(418)

    @app.get('/')
    def view():
        to_import = ["main", "footage-vis", "camera", "microphone", "presets", "calibration",
                     "footage", "thread", "scene", "socket", "settings", "tracking"]
        return render_template('view.html', to_import=to_import, page_name="Main page")

    @app.get('/camera_control')
    def camera_view():
        to_import = ["main", "camera", "socket", "settings"]
        return render_template('single_page.html', name="camera", to_import=to_import,
                               page_name="Camera View")

    @app.get('/microphone_control')
    def microphone_view():
        to_import = ["main", "microphone", "socket", "settings"]
        return render_template('single_page.html', name="microphone", to_import=to_import,
                               page_name="Microphone View")

    @app.get('/presets_and_calibration')
    def presets_and_calibration_view():
        to_import = ["main", "socket", "camera", "microphone", "presets", "calibration", "settings"]
        return render_template('single_page.html', name="presets_and_calibration",
                               to_import=to_import, page_name="Presets & Calibration View")

    @app.get('/live_footage')
    def live_footage_view():
        to_import = ["main", "footage", "socket", "settings"]
        return render_template('single_page.html', name="live_footage", to_import=to_import,
                               page_name="Live Footage")

    @app.post('/camera/address/set')
    def post_set_address():
        """
        Endpoint that sets the camera address 
            camera-ip: a string in the form _._._._
            camera-port: an int value
        """
        return web_app.camera_endpoints.address_set_camera_endpoint(integration)

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
        """ 
        Endpoint that sends a command to the camera to move in an absolute direction.
            data:
                absolute-speed-x: Integer from 1 - 24, the pan speed.
                absolute-speed-y: Integer from 1 - 20, the tilt speed.
                absolute-degrees-x: Float from -170 - 170, the amount of degrees to pan by.
                absolute-degrees-y: Float from -30 - 90, the amount of degrees to tilt by.
        """
        return web_app.camera_endpoints.move_absolute_camera_endpoint(integration)

    @app.post('/camera/move/relative')
    def post_move_relative():
        """ 
        Endpoint that sends a command to the camera to move in a relative direction.
            data:
                relative-speed-x: Integer from 1 - 24, the pan speed.
                relative-speed-y: Integer from 1 - 20, the tilt speed.
                relative-degrees-x: Float from -170 - 170, the amount of degrees to pan by.
                relative-degrees-y: Float from -30 - 90, the amount of degrees to tilt by.
        """
        return web_app.camera_endpoints.move_relative_camera_endpoint(integration)

    @app.post('/camera/move/vector')
    def post_move_vector():
        """ 
        Endpoint that sends a command to the camera to move in a vector direction.
            data:
                vector-speed-x: Integer from 1 - 24, the pan speed.
                vector-speed-y: Integer from 1 - 20, the tilt speed.
                vector-x: Float representing the x-coordinate of the direction vector.
                vector-y: Float representing the y-coordinate (height) of the direction vector.
                vector-z: Float representing the z-coordinate of the direction vector.
        """
        return web_app.camera_endpoints.move_vector_camera_endpoint(integration)

    @app.post('/camera/move/home')
    def post_home():
        """
        Endpoint to move the camera to its home direction [0,0,1]
        """
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

    @app.post('/microphone/address/set')
    def set_microphone_address():
        return web_app.microphone_endpoints.address_set_microphone_endpoint(integration)

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
        """ 
        Endpoint that saves a preset to the preset collection
            data:
                camera-direction-alpha: Float from -170 - 170 representing the yaw of the camera
                camera-direction-beta: Float from -30 - 90 representing the pitch of the camera
                camera-zoom-value: Integer with the zoom value (0-16384)
                mic-direction-x: Float representing the x-coordinate of the direction vector.
                mic-direction-y: Float representing the y-coordinate of the direction vector.
                mic-direction-z: Float representing the z-coordinate of the direction vector.
                
        """
        return web_app.preset_locations_endpoints.add_preset_location(integration)

    @app.post('/preset/edit')
    def edit_preset():
        """ 
        Endpoint that edits a preset in the preset collection
            data:
                camera-direction-alpha: Float from -170 - 170 representing the yaw of the camera
                camera-direction-beta: Float from -30 - 90 representing the pitch of the camera
                camera-zoom-value: Integer with the zoom value (0-16384)
                mic-direction-x: Float representing the x-coordinate of the direction vector.
                mic-direction-y: Float representing the y-coordinate of the direction vector.
                mic-direction-z: Float representing the z-coordinate of the direction vector.
                
        """
        return web_app.preset_locations_endpoints.edit_preset_location(integration)

    @app.post('/preset/remove')
    def remove_preset():
        """
        Endpoint that removes the given preset from the preset collection
            preset-name: a string name for the preset
        """
        return web_app.preset_locations_endpoints.remove_preset_location(integration)

    @app.get('/preset/get_list')
    def get_preset_list():
        """
        Endpoint that returns the list of all saved presets
            Returns:
                preset-list: list of all presets in a json format
        """
        return web_app.preset_locations_endpoints.get_preset_list(integration)

    @app.get('/preset/info/<preset_name>')
    def get_preset_info(preset_name):
        """
        Endpoint that returns the information for a given preset
            Returns:
                position-alpha-value: Float from -170 - 170 representing the yaw of the camera
                position-beta-value: Float from -30 - 90 representing the pitch of the camera
                zoom-value: Integer with the zoom value (0-16384)
                microphone-direction: a 3D vector (array) of floats [x, y, z]
        """
        return web_app.preset_locations_endpoints.get_preset_info(integration, preset_name)

    @app.post('/preset/point')
    def point_to_preset():
        """
        Endpoint that points the camera to the closest found preset
        """
        return web_app.preset_locations_endpoints.point_to_closest_preset(integration)

    @app.get('/preset/track')
    def preset_tracker():
        """
        Endpoint that changes the tracking to use the preset model
        """
        return web_app.tracking_endpoints.track_presets(integration)

    @app.get('/hybrid/track')
    def hybrid_tracker():
        """
        Endpoint that changes the tracking to use the hybrid model
        """
        return web_app.tracking_endpoints.track_hybrid(integration)

    @app.post('/calibration/add_directions_to_speaker')
    def add_calibration_speaker():
        """
        Endpoint that adds the camera direction towards a new calibration point
            position-alpha-value: Float from -170 - 170 representing the yaw of the camera
            position-beta-value: Float from -30 - 90 representing the pitch of the camera
        """
        return web_app.calibration_endpoints.add_calibration_speaker(integration)

    @app.post('/calibration/add_direction_to_mic')
    def add_calibration_mic():
        """
        Endpoint that adds the direction from the camera towards the microphone
            data: a 3D vector (array) of floats [x, y, z]
        """
        return web_app.calibration_endpoints.add_calibration_to_mic(integration)

    @app.post('/calibration/reset')
    def reset_calibration():
        """
        Endpoint that resets the calibration to the default values
        """
        return web_app.calibration_endpoints.reset_calibration(integration)

    @app.get('/calibration/is_set')
    def calibration_is_set():
        """
        Endpoint that checks whether the calibration is completed and all the needed vectors are calculated
            Returns: 
                is_set: boolean value
        """
        return web_app.calibration_endpoints.is_calibrated(integration)

    @app.get('/calibration/camera')
    def calibration_get_cam_coords():
        """
        Endpoint that calculates the relative coordinates of the camera in relation to the microphone
            Returns:    
                camera-coords: a 3D array of floats [x, y, z]
        """
        return web_app.calibration_endpoints.get_calibration(integration)

    @app.get('/calibration/track')
    def continuous_tracker():
        """
        Endpoint that changes the tracking to use the audio model
        """
        return web_app.tracking_endpoints.track_continuously(integration)
    @app.get('/calibration/track/no/zoom')
    def continuous_tracker_without_adaprive_zoom():
        """
        Endpoint that changes the tracking to use the audio model without adaptive zooming
        """
        return web_app.tracking_endpoints.track_continuously_without_adaptive_zooming(integration)

    @app.get('/calibration/number-of-calibrated')
    def number_of_calibrated():
        """
        Endpoint that returns the number of calibration points
            Returns: 
                speaker-points-length: an int value

        """
        return web_app.calibration_endpoints.get_number_of_speaker_points(integration)

    @app.post('/navigate/camera')
    def navigate_camera():
        """
        Endpoint that navigates the camera so that the clicked pixel is centered in the frame
            data:
                x-pos: a float value in the range [0:1]
                y-pos: a float value in the range [0:1]
        """
        return web_app.camera_endpoints.navigate_camera(integration)

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

    @app.get('/object/track')
    def object_tracking_start():
        """
        Endpoint that changes the tracking to use the object tracking model
        """
        return web_app.tracking_endpoints.track_object_continuously(integration)

    @app.post('/thread/start')
    def thread_start():
        """
        Endpoint that starts the tracking endpoint
        """
        return web_app.tracking_endpoints.start_thread_endpoint(integration)

    @app.post('/thread/stop')
    def thread_stop():
        """
        Endpoint that stops the tracking endpoint
        """
        return web_app.tracking_endpoints.stop_thread_endpoint(integration)

    @app.get('/thread/running')
    def thread_is_running():
        """
        Endpoint that checks whether the tracking thread is running
            Returns:
                is-running: a boolean value
        """
        return web_app.tracking_endpoints.is_running_endpoint(integration)

    @app.get('/thread/value')
    def thread_value():
        """
        Endpoint that returns the thread value (for testing purposes only)
            Returns: 
                value: NONE if the thread is nonexistent or and int value otherwise
        """
        if integration.thread is None:
            return make_response(jsonify({"value": "NONE"}), 200)
        print(integration.thread.value)
        return make_response(jsonify({"value": integration.thread.value}), 200)

    @app.post('/update/microphone')
    def thread_microphone():
        """
        Endpoint that updates the microphone data in the WebUI
        """
        return web_app.tracking_endpoints.update_microphone(integration)

    @app.post('/update/camera')
    def thread_camera():
        """
        Endpoint that updates the camera data in the WebUI
        """
        return web_app.tracking_endpoints.update_camera(integration)

    @integration.ws.on("request-frame")
    def camera_frame_requested(message):
        web_app.footage.emit_frame(integration)

    @app.post('/update/calibration')
    def thread_calibration():
        """
        Endpoint that updates the calibration data in the WebUI
        """
        return web_app.tracking_endpoints.update_calibration(integration)
    # Info-thread section

    @app.post('/info-thread/start')
    def info_thread_start():
        """
        Endpoint that starts the thread that updates all the dynamic data
        """
        integration.info_threads_event.value = 1
        return make_response(jsonify({}), 200)

    @app.post('/info-thread/stop')
    def info_thread_stop():
        """
        Endpoint that stops the thread that updates all the dynamic data
        """
        integration.info_threads_event.value = 0
        return make_response(jsonify({}), 200)

    @app.get('/settings/get')
    def settings_get():
        """
        Endpoint that gets the system settings
            Returns: 
                camera-ip: a string address
                camera-port: an int value
                microphone-ip: a string address
                microphone-port: an int value
                microphone-thresh: an int value
                filepath: a path string
        """
        return web_app.settings_endpoints.get(integration)

    @app.post('/settings/set')
    def settings_set():
        """
        Endpoint that sets the following system settings
            camera-ip: a string address
            camera-port: an int value
            microphone-ip: a string address
            microphone-port: an int value
            microphone-thresh: an int value
            filepath: a path string
        """
        return web_app.settings_endpoints.set_settings(integration)

    @integration.ws.on("connected")
    def settings_not_set(data):
        if not integration.no_settings_sent:  # prompt user to set up if no settings file found
            integration.ws.emit("no-settings", data)
        else:
            integration.ws.emit("yes-settings", {})

    def sigterm_handler(_signo, _stack_frame):
        close_running_threads(integration)

    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    return app


if __name__ == "__main__":
    application = create_app()
