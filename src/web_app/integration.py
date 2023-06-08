from threading import Event, Thread
from os import getenv
from time import sleep
from multiprocessing import Value
from yaml import load, dump
try:  # https://pyyaml.org/wiki/PyYAMLDocumentation
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
import requests
import cv2
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI, converter, ResponseCode
from avonic_camera_api.footage import FootageThread
from avonic_camera_api.camera_adapter import CameraSocket
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import MicrophoneSocket
from avonic_speaker_tracker.preset_model.PresetModel import PresetModel
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel


class GeneralController:
    def __init__(self):
        # self.event is part of the while loop in UpdateThread. When 0 - stops the while loop.
        self.event = Value("i", 0, lock=False)

        # self.info_threads_event is part of the info-threads
        # and indicates whether update should be performed.
        # when 0 - doesn't perform the update, when 1 - performs the update
        self.info_threads_event = Value("i", 0, lock=False)

        self.footage_thread_event = Event()

        # self.info_threads_break used to completely destroy info-thread, and not just pause
        # Used for safe finish of the program, for safe destruction.
        # When 1 - finishes the thread ASAP.
        self.info_threads_break = Value("i", 0, lock=False) # THIS IS ONLY FOR DESTROYING THREADS

        # Update thread field
        self.thread = None
        # Footage thread field
        self.footage_thread = None

        # URL of the server
        self.url = '127.0.0.1:5000'

        # Camera and microphone APIs
        self.cam_sock = None  # Only for testing
        self.cam_api = None
        self.mic_api = None

        # Secret for cookies and websocket
        self.secret = None
        self.ws = None

        # Filepath for calibration and presets files
        self.filepath: str = ""

        # Models, to record all updates onto a disk
        self.audio_model = None
        self.preset_model = None

        # Video related fields
        self.camera_footage = None
        self.video = None

        # Info-threads
        self.thread_mic = None
        self.thread_cam = None

        # Indicates which model should be used, check UpdateThread
        self.preset = Value("i", 0, lock=False)

    def load_env(self) -> None:
        """Performs load procedure of all the specified parameters.
        """
        self.preset = Value("i", 0, lock=False)
        url = getenv("SERVER_ADDRESS")
        if url is not None:
            self.url = url

        # Load settings file
        try:
            with open("settings.yaml", "r") as f:
                settings = load(f, Loader=Loader)
        except IOError as e:
            print("Could not open settings.yaml file, proceeding without it.")
            print(e)
            settings = {
                "camera-ip": "0.0.0.0",
                "camera-port": 52381,
                "microphone-ip": "0.0.0.0",
                "microphone-port": 45,
                "microphone-thresh": -55,
                "filepath": "",
                "secret-key": "test"
            }

        # Setup camera API
        cam_addr = None
        cam_port = settings["camera-port"]
        if cam_port is not None:
            cam_addr = (settings["camera-ip"], int(cam_port))
            if cam_addr is not None:
                self.cam_api = CameraAPI(CameraSocket(address=cam_addr))

        # Setup microphone API
        mic_addr = None
        mic_port = settings["microphone-port"]
        print(mic_port, mic_port is None)
        if mic_port is not None:
            mic_addr = (settings["microphone-ip"], int(mic_port))
            if mic_addr is not None:
                self.mic_api = MicrophoneAPI(MicrophoneSocket(address=mic_addr), int(settings["microphone-thresh"]))

        # Setup secret
        self.secret = settings["secret-key"]

        # Get filepath
        filepath = settings["filepath"]
        if filepath is not None:
            self.filepath = str(filepath)

        # Initialize models
        self.audio_model = AudioModel(filename=self.filepath + "calibration.json")
        self.preset_model = PresetModel(filename=self.filepath + "presets.json")

        # Initialize footage thread
        if cam_addr is not None:
            self.video = cv2.VideoCapture('rtsp://' + settings["camera-ip"] + ':554/live/av0')# pragma: no mutate
            self.footage_thread = FootageThread(self.video,self.footage_thread_event)# pragma: no mutate
            self.footage_thread.start() # pragma: no mutate

        # Initialize camera and microphone info threads
        self.info_threads_event.value = 0
        self.info_threads_break.value = 0 # THIS IS ONLY FOR DESTROYING THREADS
        if mic_addr is not None:
            self.thread_mic = Thread(target=self.send_update,
                args=(self.get_mic_info, '/update/microphone'))
            self.thread_mic.start()
        if cam_addr is not None:
            self.thread_cam = Thread(target=self.send_update,
                args=(self.get_cam_info, '/update/camera'))
            self.thread_cam.start()

    def save(self):
        """
        Saves current settings to `settings.yaml`

        Returns:
            True on success
            False on error
        """
        try:
            with open("settings.yaml", "w") as f:
                cam_addr = self.cam_api.camera.address
                mic_addr = self.mic_api.sock.address
                data = {
                    "camera-ip": cam_addr[0],
                    "camera-port": cam_addr[1],
                    "microphone-ip": mic_addr[0],
                    "microphone-port": mic_addr[1],
                    "microphone-thresh": self.mic_api.threshold,
                    "filepath": self.filepath,
                    "secret-key": self.secret
                }
                dump(data, f, Dumper=Dumper)
            return True
        except IOError as e:
            print("Error while writing settings file!")
            print(e)
            return False

    def __del__(self):
        self.preset.value = 0  # pragma: no mutate
        self.footage_thread_event.set() # pragma: no mutate
        self.info_threads_break.value = 1 # pragma: no mutate

        try: # pragma: no mutate
            self.thread_mic.join() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread for microphone") # pragma: no mutate
        try: # pragma: no mutate
            self.thread_cam.join() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread for camera") # pragma: no mutate
        try: # pragma: no mutate
            self.footage_thread.join() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread for footage") # pragma: no mutate
        try: # pragma: no mutate
            self.video.release() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread for video") # pragma: no mutate
        try: # pragma: no mutate
            cv2.destroyAllWindows() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread for cv2") # pragma: no mutate

    def load_mock(self):
        # This function is used to initialize integration in testing.
        cam_addr = ('0.0.0.0', 52381)
        mic_addr = ('0.0.0.0', 45)
        self.cam_api = CameraAPI(CameraSocket(sock=self.cam_sock, address=cam_addr))
        self.mic_api = MicrophoneAPI(MicrophoneSocket(address=mic_addr), -55)
        self.audio_model = AudioModel()
        self.preset_model = PresetModel()
        self.thread = None

    def copy(self, new_controller):
        self.event = new_controller.event
        self.thread = new_controller.thread
        self.cam_api = new_controller.cam_api
        self.mic_api = new_controller.mic_api
        self.ws = new_controller.ws
        self.audio_model = AudioModel()
        self.preset_model = PresetModel()

    def set_mic_api(self, new_mic_api) -> None:
        self.mic_api = new_mic_api

    def set_cam_api(self, new_cam_api) -> None:
        self.cam_api = new_cam_api

    def get_model_based_on_choice(self) -> TrackingModel:
        if self.preset.value == 0:
            return self.preset_model
        return self.audio_model

    def get_mic_info(self) -> dict:
        """ Get information about the microphone.
        This function is used by microphone info-thread.

        Returns: dictionary with "microphone-direction" and "microphone-speaking" entries
        """
        return {
            "microphone-direction": list(self.mic_api.get_direction()),
            "microphone-speaking": self.mic_api.is_speaking()
        }

    def get_cam_info(self) -> dict:
        """ Get the direction of the camera.
        This function is used by camera info-thread.

        Returns: dictionary with "camera-direction", "camera-video", and "zoom-value" entries
        """
        direction = self.cam_api.get_direction()
        zoom = self.cam_api.get_zoom()
        if isinstance(direction, ResponseCode):
            direction = np.array([0.0, 0.0, 1.0])
        if isinstance(zoom, ResponseCode):
            zoom = np.array(0)
        angles = converter.vector_angle(direction)
        if not isinstance(zoom, int):
            zoom = 0
        return {
            "camera-direction": {
                "position-alpha-value": angles[0],
                "position-beta-value": angles[1]
            },
            "zoom-value": zoom,
            "camera-video": self.cam_api.video
        }

    def send_update(self, data, path: str) -> None:
        """ This method is used as a body of the info-thread. Function that performs
        GET requests to microphone or camera for information retrieval is passed as an arguments.
        After the information is obtained, send an HTTP request to the Flask server
        to update the webpages, by emitting WebSocket message.

        self.info_threads_break - responsible for finishing the thread.
        While 0 - will continue iterating. If 1 - last iteration will be performed.

        self.info_threads_event.value - responsible for whether the request
        for new information should be performed.

        0 - shouldn't, 1 - should.

        By this, we achieve the fact that info-threads are always running in the background,
        so the information retrieval can be paused, but not the thread itself.

        Args:
            data: The data in dictionary format
            path: The path to send to
        """
        print("Info-thread is started and will send updates to " + path)
        flag = True
        while flag:
            if self.info_threads_break.value == 1:
                flag = False
            if self.info_threads_event.value != 0:
                d = data()
                response = requests.post('http://' + self.url + path, json=d)
                if response.status_code != 200:
                    print("Could not update flask at path " + path)
            sleep(0.3)
        print("Closing " + path + " updater thread")


def verify_address(address) -> None:
    try:
        assert 0 <= address[1] <= 65535
        assert 0 <= int(address[0].split(".")[0]) <= 255 and \
               0 <= int(address[0].split(".")[1]) <= 255 and \
               0 <= int(address[0].split(".")[2]) <= 255 and \
               0 <= int(address[0].split(".")[3]) <= 255
    except AssertionError:
        print("ERROR: Address " + address + " is invalid!")


def close_running_threads(integration_passed) -> None:
    """This method is used for safe finish of the Flask and all of our threads."""
    integration_passed.footage_thread_event.set() # pragma: no mutate
    integration_passed.info_threads_break.value = 1 # pragma: no mutate

    integration_passed.thread_mic.join() # pragma: no mutate
    integration_passed.thread_cam.join() # pragma: no mutate
    integration_passed.footage_thread.join() # pragma: no mutate
    cv2.destroyAllWindows() # pragma: no mutate
    integration_passed.video.release() # pragma: no mutate
    raise SystemExit # pragma: no mutate
