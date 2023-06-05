from threading import Event, Thread
from os import getenv
from time import sleep
from dotenv import load_dotenv
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
from multiprocessing import Value, Array

class GeneralController:
    def __init__(self):
        self.event = Value("i", 0, lock=False)
        self.info_threads_event = Value("i", 0, lock=False)
        self.footage_thread_event = Event()
        self.info_threads_break = Value("i", 0, lock=False) # THIS IS ONLY FOR DESTROYING THREADS
        self.thread = None
        self.footage_thread = None
        self.url = '127.0.0.1:5000'
        self.cam_sock = None  # Only for testing
        self.cam_api = None
        self.mic_api = None
        self.secret = None
        self.ws = None
        self.audio_model = None
        self.preset_model = None
        self.model = None
        self.camera_footage = None
        self.video = None
        self.thread_mic = None
        self.thread_cam = None
        self.preset = Value("i", 0, lock=False)

    def load_env(self):
        self.preset = Value("i", 0, lock=False)
        url = getenv("SERVER_ADDRESS")
        if url is not None:
            self.url = url
        load_dotenv()
        # Setup camera API
        cam_addr = (getenv("CAM_IP"), int(getenv("CAM_PORT")))
        verify_address(cam_addr)
        self.cam_api = CameraAPI(CameraSocket(address=cam_addr))

        # Setup microphone API
        mic_addr = (getenv("MIC_IP"), int(getenv("MIC_PORT")))
        verify_address(mic_addr)
        self.mic_api = MicrophoneAPI(MicrophoneSocket(address=mic_addr), int(getenv("MIC_THRESH")))

        # Setup secret
        self.secret = getenv("SECRET_KEY")

        # Initialize models
        self.audio_model = AudioModel(filename="calibration.json")
        self.preset_model = PresetModel(filename="presets.json")

        # Initialize footage thread
        self.video = cv2.VideoCapture('rtsp://' + getenv("CAM_IP") + ':554/live/av0') # pragma: no mutate
        self.footage_thread = FootageThread(self.video, self.footage_thread_event) # pragma: no mutate
        self.footage_thread.start() # pragma: no mutate

        # Initialize camera and microphone info threads
        self.info_threads_event.value = 0
        self.info_threads_break.value = 0 # THIS IS ONLY FOR DESTROYING THREADS
        self.thread_mic = Thread(target=self.send_update,
            args=(self.get_mic_info, '/update/microphone'))
        self.thread_cam = Thread(target=self.send_update,
            args=(self.get_cam_info, '/update/camera'))
        self.thread_mic.start()
        self.thread_cam.start()

    def __del__(self):
        self.preset.value = 0 # pragma: no mutate
        self.footage_thread_event.set() # pragma: no mutate
        self.info_threads_break.value = 1 # pragma: no mutate

        try: # pragma: no mutate
            self.thread_mic.join() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread") # pragma: no mutate
        try: # pragma: no mutate
            self.thread_cam.join() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread") # pragma: no mutate
        try: # pragma: no mutate
            self.footage_thread.join() # pragma: no mutate
        except: # pragma: no mutate 
            print("Trying to destruct None thread") # pragma: no mutate
        try: # pragma: no mutate 
            self.video.release() # pragma: no mutate
        except: # pragma: no mutate 
            print("Trying to destruct None thread") # pragma: no mutate
        try: # pragma: no mutate
            cv2.destroyAllWindows() # pragma: no mutate
        except: # pragma: no mutate
            print("Trying to destruct None thread") # pragma: no mutate

    def load_mock(self):
        cam_addr = ('0.0.0.0', 52381)
        mic_addr = ('0.0.0.0', 45)
        self.cam_api = CameraAPI(CameraSocket(sock=self.cam_sock, address=cam_addr))
        self.mic_api = MicrophoneAPI(MicrophoneSocket(address=mic_addr), 55)
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

    def set_mic_api(self, new_mic_api):
        self.mic_api = new_mic_api

    def set_cam_api(self, new_cam_api):
        self.cam_api = new_cam_api

    def get_model_based_on_choice(self):
        if self.preset.value == 0:
            return self.preset_model
        return self.audio_model

    def get_mic_info(self):
        """ Get information about the microphone.
        """
        return {
            "microphone-direction": list(self.mic_api.get_direction()),
            "microphone-speaking": self.mic_api.is_speaking()
        }

    def get_cam_info(self):
        """ Get the direction of the camera.
        """
        direction = self.cam_api.get_direction()
        zoom = self.cam_api.get_zoom()
        if isinstance(direction, ResponseCode):
            direction = np.array([0, 0, 1])
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

    def send_update(self, data, path: str):
        """ Send an HTTP request to the flask server to update the webpages.

        Args:
            data: The data in dictionary format
            path: The path to send to
        """
        print("Info-thread start and will send updates to " + path)
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


def verify_address(address):
    try:
        assert 0 <= address[1] <= 65535
        assert 0 <= int(address[0].split(".")[0]) <= 255 and \
               0 <= int(address[0].split(".")[1]) <= 255 and \
               0 <= int(address[0].split(".")[2]) <= 255 and \
               0 <= int(address[0].split(".")[3]) <= 255
    except AssertionError:
        print("ERROR: Address " + address + " is invalid!")


def close_running_threads(integration_passed):
    integration_passed.footage_thread_event.set() # pragma: no mutate
    integration_passed.info_threads_break.value = 1 # pragma: no mutate

    integration_passed.thread_mic.join() # pragma: no mutate
    integration_passed.thread_cam.join() # pragma: no mutate
    integration_passed.footage_thread.join() # pragma: no mutate
    cv2.destroyAllWindows() # pragma: no mutate
    integration_passed.video.release() # pragma: no mutate
    raise SystemExit # pragma: no mutate
