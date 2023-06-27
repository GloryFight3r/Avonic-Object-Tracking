import signal
from flask import Flask, jsonify, abort, render_template, make_response
from flask_socketio import SocketIO
import maat_web_app.camera_endpoints
import maat_web_app.microphone_endpoints
import maat_web_app.preset_locations_endpoints
import maat_web_app.footage
import maat_web_app.calibration_endpoints
import maat_web_app.tracking_endpoints
import maat_web_app.settings_endpoints
from maat_web_app.integration import GeneralController, close_running_threads

# While testing to keep the log clean
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
        """
        Render the main page of the WebUI.
        This page includes everything our application has to offer in one neatly organised package
        """
        to_import = ["main", "footage-vis", "camera", "microphone", "presets", "calibration",
                     "footage", "thread", "scene", "socket", "settings", "tracking"]
        return render_template('view.html', to_import=to_import, page_name="Main page")

    @app.get('/camera_control')
    def camera_view():
        """
        Render a page that includes only the camera controls.
        """
        to_import = ["main", "camera", "socket", "settings"]
        return render_template('single_page.html', name="camera", to_import=to_import,
                               page_name="Camera View")

    @app.get('/microphone_control')
    def microphone_view():
        """
        Render a page that includes only the microphone information.
        That means the buttons to get its direction and whether someone is currently speaking.
        """
        to_import = ["main", "microphone", "socket", "settings"]
        return render_template('single_page.html', name="microphone", to_import=to_import,
                               page_name="Microphone View")

    @app.get('/presets_and_calibration')
    def presets_and_calibration_view():
        """
        Render a page that includes only set-up for presets and calibration.
        """
        to_import = ["main", "socket", "camera", "microphone", "presets", "calibration", "settings"]
        return render_template('single_page.html', name="presets_and_calibration",
                               to_import=to_import, page_name="Presets & Calibration View")

    @app.get('/live_footage')
    def live_footage_view():
        """
        Render a page that includes only the video stream from the camera.
        :return:
        """
        to_import = ["main", "footage", "socket", "settings"]
        return render_template('single_page.html', name="live_footage", to_import=to_import,
                               page_name="Live Footage")

    @app.post('/camera/address/set')
    def post_set_address():
        """
        Endpoint that sets the camera network settings.
            form:
                "camera-ip": the address of the connected camera
                "camera-port": the camera port
                "camera-http-port": the HTTP port of the camera
            return:
                HTTP code corresponds to the camera response:
                    "message": description of the received response code from the camera
                Possible HTTP 400: invalid supplied values
                    "message": "Invalid address!"
        """
        return maat_web_app.camera_endpoints.address_set_camera_endpoint(integration)

    @app.post('/camera/reboot')
    def post_reboot():
        """
        Endpoint that reboots the camera.
            return:
                HTTP 200: success, empty message
                Other HTTP codes:
                    HTTP code corresponds to the camera response
                    "message": description of the received response code from the camera
        """
        return maat_web_app.camera_endpoints.reboot_camera_endpoint(integration)

    @app.post('/camera/on')
    def post_turn_on_camera():
        """
        Endpoint that turns the camera's video on.
            return:
                HTTP 200: success, empty message
                Other HTTP codes:
                    HTTP code corresponds to the camera response
                    "message": description of the received response code from the camera
        """
        return maat_web_app.camera_endpoints.turn_on_camera_endpoint(integration)

    @app.post('/camera/off')
    def post_off():
        """
        Endpoint that turns the camera's video off.
            return:
                HTTP 200: success, empty message
                Other HTTP codes:
                    HTTP code corresponds to the camera response
                    "message": description of the received response code from the camera
        """
        return maat_web_app.camera_endpoints.turn_off_camera_endpoint(integration)

    @app.post('/camera/move/absolute')
    def post_move_absolute():
        """
        Endpoint that sends a command to the camera to point in a direction relative to the home one.
            form:
                "absolute-speed-x": Integer from 1 - 24, the pan speed.
                "absolute-speed-y": Integer from 1 - 20, the tilt speed.
                "absolute-degrees-x": Float from -170 - 170, the amount of degrees to pan by.
                "absolute-degrees-y": Float from -30 - 90, the amount of degrees to tilt by.
            return:
                HTTP code corresponds to the camera response:
                    "message": description of the received response code from the camera
                Possible HTTP 400: assertion error of validity of supplied values
        """
        return maat_web_app.camera_endpoints.move_absolute_camera_endpoint(integration)

    @app.post('/camera/move/relative')
    def post_move_relative():
        """
        Endpoint that sends a command to the camera to point in a direction relative to the current one.
            form:
                "relative-speed-x": Integer from 1 - 24, the pan speed.
                "relative-speed-y": Integer from 1 - 20, the tilt speed.
                "relative-degrees-x": Float from -170 - 170, the amount of degrees to pan by.
                "relative-degrees-y": Float from -30 - 90, the amount of degrees to tilt by.
            return:
                HTTP code corresponds to the camera response:
                    "message": description of the received response code from the camera
                Possible HTTP 400: assertion error of validity of supplied values
        """
        return maat_web_app.camera_endpoints.move_relative_camera_endpoint(integration)

    @app.post('/camera/move/vector')
    def post_move_vector():
        """
        Same as `/camera/move/absolute` but a vector is used as a direction instead of two angles.
            form:
                "vector-speed-x": Integer from 1 - 24, the pan speed.
                "vector-speed-y": Integer from 1 - 20, the tilt speed.
                "vector-x": Float representing the x-coordinate of the direction vector.
                "vector-y": Float representing the y-coordinate (height) of the direction vector.
                "vector-z": Float representing the z-coordinate of the direction vector.
            return:
                HTTP code corresponds to the camera response:
                    "message": description of the received response code from the camera
                Possible HTTP 400: assertion error of validity of supplied values
        """
        return maat_web_app.camera_endpoints.move_vector_camera_endpoint(integration)

    @app.post('/camera/move/home')
    def post_home():
        """
        Endpoint to move the camera to its home direction `[0, 0, 1]`.
            return:
                HTTP code corresponds to the camera response
                "message": description of the received response code from the camera
        """
        return maat_web_app.camera_endpoints.move_home_camera_endpoint(integration)

    @app.post('/camera/move/stop')
    def stop():
        """
        Endpoint to stop all the camera's movement.
            return:
                HTTP code corresponds to the camera response
                "message": description of the received response code from the camera
        """
        return maat_web_app.camera_endpoints.move_stop_camera_endpoint(integration)

    @app.get('/camera/zoom/get')
    def get_zoom():
        """
        Endpoint to get the zoom value of the camera.
            return:
                In case of an error:
                    HTTP code corresponds to the camera response
                    "message": description of the received response code from the camera
                In case of success:
                    HTTP 200
                    "zoom-value": Integer in range [0, 16384], the value of the zoom
        """
        return maat_web_app.camera_endpoints.zoom_get_camera_endpoint(integration)

    @app.post('/camera/zoom/set')
    def set_zoom():
        """
        Endpoint to set the zoom value of the camera.
            form:
                "zoom-value": Integer in range [0, 16384], the value of the zoom
            return:
                HTTP code corresponds to the camera response:
                    "message": description of the received response code from the camera
                Possible HTTP 400: assertion error of validity of supplied values
        """
        return maat_web_app.camera_endpoints.zoom_set_camera_endpoint(integration)

    @app.get('/camera/position/get')
    def get_position():
        """
        Endpoint to get the current pan and tilt values of the camera.
            return:
                In case of an error:
                    HTTP code corresponds to the camera response
                    "message": description of the received response code from the camera
                In case of success:
                    HTTP 200
                    "position-alpha-value": pan value of the camera
                    "position-beta-value": tilt value of the camera
        """
        return maat_web_app.camera_endpoints.position_get_camera_endpoint(integration)

    @app.post('/microphone/address/set')
    def set_microphone_address():
        """
        Endpoint that sets the camera network settings.
            form:
                "microphone-ip": a string, the address of the microphone
                "microphone-port": the microphone port
            return:
                HTTP 200 or 400:
                    Text of the return message from the microphone
                Possible HTTP 400: not valid supplied address or port:
                    "message": "Invalid address!"
        """
        return maat_web_app.microphone_endpoints.address_set_microphone_endpoint(integration)

    @app.post('/microphone/height/set')
    def set_height():
        """
        Endpoint to set the height of the microphone above the speaker plane.
            form:
                "microphone-height": float representing value to be set
            return:
                HTTP 200:
                    "microphone-height": with the value that was set
                HTTP 504:
                    "message": error message returned from the microphone
        """
        return maat_web_app.microphone_endpoints.height_set_microphone_endpoint(integration)

    @app.get('/microphone/direction')
    def get_direction():
        """
        Endpoint to get the current direction to the loudest noise in the room from the microphone
            return:
                HTTP 200:
                    "microphone-direction": list with 3 float values representing direction of the speaker
                HTTP 504:
                    "message": error message returned from the microphone
        """
        return maat_web_app.microphone_endpoints.direction_get_microphone_endpoint(integration)

    @app.get('/microphone/speaker/direction')
    def get_speaker_direction():
        """
        Endpoint to get the direction of the active speaker. Used for setting up presets and calibrating.
        Actively loops polling data from the microphone, waits for 5 seconds.
        If nobody has spoken in 5 seconds - returns current direction from the microphone.
            return:
                HTTP 200:
                    "microphone-direction": list with 3 float values representing direction of the speaker
                HTTP 504:
                    "message": error message returned from the microphone
        """
        return maat_web_app.microphone_endpoints.get_speaker_direction_endpoint(integration)

    @app.get('/microphone/speaking')
    def get_speaking():
        """
        Endpoint to inquire whether anyone is speaking.
            return:
                HTTP 200:
                    "microphone-speaking": boolean representing is some someone speaking at the moment
                HTTP 504:
                    "message": error message returned from the microphone
        """
        return maat_web_app.microphone_endpoints.speaking_get_microphone_endpoint(integration)

    @app.post('/preset/add')
    def add_preset():
        """
        Endpoint that saves a preset to the preset collection.
            form:
                "preset-name": Unique string representing the name of the preset.
                "camera-direction-alpha": Float from -170 - 170 representing the yaw of the camera
                "camera-direction-beta": Float from -30 - 90 representing the pitch of the camera
                "camera-zoom-value": Integer with the zoom value (0-16384)
                "mic-direction-x": Float representing the x-coordinate of the direction vector.
                "mic-direction-y": Float representing the y-coordinate of the direction vector.
                "mic-direction-z": Float representing the z-coordinate of the direction vector.
            return:
                HTTP 200: success, empty message
                HTTP 400: invalid supplied values, empty message

        """
        return maat_web_app.preset_locations_endpoints.add_preset_location(integration)

    @app.post('/preset/edit')
    def edit_preset():
        """
        Endpoint that edits a preset in the preset collection.
            form:
                "preset-name": String representing the name of the preset
                "camera-direction-alpha": Float from -170 - 170 representing the yaw of the camera
                "camera-direction-beta": Float from -30 - 90 representing the pitch of the camera
                "camera-zoom-value": Integer with the zoom value (0-16384)
                "mic-direction-x": Float representing the x-coordinate of the direction vector.
                "mic-direction-y": Float representing the y-coordinate of the direction vector.
                "mic-direction-z": Float representing the z-coordinate of the direction vector.
            return:
                HTTP 200: success, empty message
                HTTP 400: invalid supplied values, empty message

        """
        return maat_web_app.preset_locations_endpoints.edit_preset_location(integration)

    @app.post('/preset/remove')
    def remove_preset():
        """
        Endpoint that removes the given preset from the preset collection.
            form:
                "preset-name": string name for the preset
            return:
                HTTP 200: success, empty message
                HTTP 400: invalid supplied values, empty message
        """
        return maat_web_app.preset_locations_endpoints.remove_preset_location(integration)

    @app.get('/preset/get_list')
    def get_preset_list():
        """
        Endpoint that returns the list of all saved presets.
            return:
                "preset-list": list of all presets in a json format
        """
        return maat_web_app.preset_locations_endpoints.get_preset_list(integration)

    @app.get('/preset/info/<preset_name>')
    def get_preset_info(preset_name):
        """
        Endpoint that returns information about a given preset.
            return:
                In case of success:
                    HTTP 200
                    "position-alpha-value": Float from -170 - 170 representing the yaw of the camera
                    "position-beta-value": Float from -30 - 90 representing the pitch of the camera
                    "zoom-value": Integer with the zoom value (0-16384)
                    "microphone-direction": a 3D vector (array) of floats [x, y, z]
                In case of an error:
                    HTTP 400, empty message
        """
        return maat_web_app.preset_locations_endpoints.get_preset_info(integration, preset_name)

    @app.post('/preset/point')
    def point_to_preset():
        """
        Endpoint that points the camera to the closest preset available.
        Performs movement.
            return:
                HTTP 200, empty message
        """
        return maat_web_app.preset_locations_endpoints.point_to_closest_preset(integration)

    @app.get('/preset/track')
    def preset_tracker():
        """
        Endpoint that changes the tracking to use the preset model.
            return:
                HTTP 200
                "tracking": value representing preset model
        """
        return maat_web_app.tracking_endpoints.track_presets(integration)

    @app.get('/hybrid/track')
    def hybrid_tracker():
        """
        Endpoint that changes the tracking to use the hybrid model
            return:
                HTTP 200
                "tracking": value representing hybrid model
        """
        return maat_web_app.tracking_endpoints.track_hybrid(integration)


    @app.post('/calibration/add_directions_to_speaker')
    def add_calibration_speaker():
        """
        Endpoint that adds the camera direction towards a new calibration point

            return:
                In case of an error:
                    "message": the exact error message
                    HTTP 504: the error code if no direction could be gotten from either the camera
                        or the microphone

                In case of a success:
                    HTTP 200: success code
        """
        return maat_web_app.calibration_endpoints.add_calibration_speaker(integration)

    @app.post('/calibration/add_direction_to_mic')
    def add_calibration_mic():
        """
        Endpoint that adds the direction from the camera towards the microphone to the calibration

            return:
                In case of a success:
                    HTTP 200: success code

                In case of an error:
                    "message": the exact error message
                    HTTP 504: the error code if no direction could be gotten from the camera
        """
        return maat_web_app.calibration_endpoints.add_calibration_to_mic(integration)

    @app.post('/calibration/reset')
    def reset_calibration():
        """
        Endpoint that resets the calibration to the default values

            return:
                HTTP 200: success code
        """
        return maat_web_app.calibration_endpoints.reset_calibration(integration)

    @app.get('/calibration/is_set')
    def calibration_is_set():
        """
        Endpoint that checks whether the calibration is completed and all the
        needed vectors are calculated

            return:
                "is_set": boolean indicating whether calibration has been completed
                HTTP 200: success code
        """
        return maat_web_app.calibration_endpoints.is_calibrated(integration)

    @app.get('/calibration/camera')
    def calibration_get_cam_coords():
        """
        Endpoint that calculates the relative coordinates of the camera in
        relation to the microphone

            return:
                "camera-coords": a 3D array of floats [x, y, z]
                HTTP 200: successfully
        """
        return maat_web_app.calibration_endpoints.get_calibration(integration)

    @app.get('/calibration/track')
    def continuous_tracker():
        """
        Endpoint that changes the tracking to use the audio model

            return:
                "tracking": the enum corresponding to the AudioModel
                HTTP 200: the model has successfully been set to the AudioModel
        """
        return maat_web_app.tracking_endpoints.track_continuously(integration)

    @app.get('/calibration/track/no/zoom')
    def continuous_tracker_without_adaptive_zoom():
        """
        Endpoint that changes the tracking to use the audio model without adaptive zooming

            return:
                "tracking": the enum corresponding to the AudioModelNoAdaptiveZoom
                HTTP 200: the model has successfully been set to the AudioModelNoAdaptiveZoom
        """
        return maat_web_app.tracking_endpoints.track_continuously_without_adaptive_zooming(integration)

    @app.get('/calibration/number-of-calibrated')
    def number_of_calibrated():
        """
        Endpoint that returns the number of calibration points

            return:
                "speaker-points-length": the amount of speaker points that have been set [0 : 3]
                HTTP 200: success code

        """
        return maat_web_app.calibration_endpoints.get_number_of_speaker_points(integration)

    @app.post('/navigate/camera')
    def navigate_camera():
        """
        Endpoint that navigates the camera so that the clicked pixel is centered in the frame
            form:
                "x-pos": a float value in the range [0:1]
                "y-pos": a float value in the range [0:1]

            return:
                In case of an error:
                    "message": the error that was thrown
                    HTTP 400: bad request, see "message" for more details
                    HTTP 409: conflict, in case the command to the camera got cancelled
                    HTTP 504: time out in the camera

                In case of a success:
                    "message": success message
                    HTTP 200: success code

        """
        return maat_web_app.camera_endpoints.navigate_camera(integration)

    @app.get('/object/track')
    def object_tracking_start():
        """
        Endpoint that changes the tracking to use the object tracking model

            return:
                "tracking": the enum corresponding to the WaitObjectAudioModel
                HTTP 200: the model has successfully been set to the WaitObjectAudioModel
        """
        return maat_web_app.tracking_endpoints.track_object_continuously(integration)

    @app.post('/thread/start')
    def thread_start():
        """
        Endpoint that starts the tracking thread

            return:
                In case of an error:
                    HTTP 403: the thread has already been started before
                In case of success:
                    HTTP 200: the thread has successfully been started
        """
        return maat_web_app.tracking_endpoints.start_thread_endpoint(integration)

    @app.post('/thread/stop')
    def thread_stop():
        """
        Endpoint that stops the tracking thread

            return:
                HTTP 200: successfully stopped the tracking thread
        """
        return maat_web_app.tracking_endpoints.stop_thread_endpoint(integration)

    @app.get('/thread/running')
    def thread_is_running():
        """
        Endpoint that checks whether the tracking thread is running. This means that the thread is
        not None and that it is alive

            return:
                "is-running": a boolean value indicating whether the thread is running or not
        """
        return maat_web_app.tracking_endpoints.is_running_endpoint(integration)

    @app.post('/update/microphone')
    def thread_microphone():
        """
        Endpoint that updates the microphone data in the WebUI

            return:
                HTTP 200: successfully updated the microphone coordinates
        """
        return maat_web_app.tracking_endpoints.update_microphone(integration)

    @app.post('/update/camera')
    def thread_camera():
        """
        Endpoint that updates the camera data in the WebUI

            return:
                HTTP 200: successfully updated the camera coordinates
        """
        return maat_web_app.tracking_endpoints.update_camera(integration)

    @integration.ws.on("request-frame")
    def camera_frame_requested(message):
        """
        Websocket endpoint that sends a new frame in base64 to the web interface
        """
        maat_web_app.footage.emit_frame(integration)

    @app.post('/info-thread/start')
    def info_thread_start():
        """
        Endpoint that starts the thread that updates all the dynamic data
        This means the current directions and more for both the camera and microphone

        return:
            HTTP 200: successfully started the info thread
        """
        integration.info_threads_event.value = 1
        return make_response(jsonify({}), 200)

    @app.post('/info-thread/stop')
    def info_thread_stop():
        """
        Endpoint that stops the thread that updates all the dynamic data

            return:
                HTTP 200: successfully stopped the info thread
        """
        integration.info_threads_event.value = 0
        return make_response(jsonify({}), 200)

    @app.get('/settings/get')
    def settings_get():
        """
        Endpoint that gets the system settings
            return:
                "camera-ip": the address of the connected camera
                "camera-port": the port of the connected camera
                "microphone-ip": the address of the connected microphone
                "microphone-port": the port of the connected microphone
                "microphone-thresh": an int value between -90 and 0 representing the preferred
                    volume threshold
                "filepath": a string representing the folder in which the settings file is stored
                HTTP 200: successfully gotten the settings
        """
        return maat_web_app.settings_endpoints.get(integration)

    @app.post('/settings/set')
    def settings_set():
        """
        Endpoint that sets the following settings to the ones given.

            form:
                "camera-ip": the address of the camera to connect to
                "camera-port": the port of the camera to connect to
                "microphone-ip": the address of the microphone to connect to
                "microphone-port": the port of the microphone to connect to
                "microphone-thresh": an int value between -90 and 0 representing the preferred
                    volume threshold
                "filepath": a string representing the folder in which to store the settings file

            return:
                In case of an error:
                    "message": description of the error that was caught
                    HTTP 400: either the threshold or the filepath were not given correctly
                    HTTP 500: an error occurred while writing to the settings file
                In case of success:
                    HTTP 200: success code
        """
        return maat_web_app.settings_endpoints.set_settings(integration)

    @integration.ws.on("connected")
    def settings_not_set(data):
        """
        WebSocket endpoint that, on a client's connection,
        causes it to open the settings menu when none are set.
        """
        if not integration.no_settings_sent:  # prompt user to set up if no settings file found
            integration.ws.emit("no-settings", data)
        else:
            integration.ws.emit("yes-settings", {})
        if integration.footage_thread_event.value == 0:
            integration.ws.emit("no-footage")

    def sigterm_handler(_signo, _stack_frame):
        close_running_threads(integration)

    signal.signal(signal.SIGINT, sigterm_handler)
    signal.signal(signal.SIGTERM, sigterm_handler)

    return app


if __name__ == "__main__":
    application = create_app()
