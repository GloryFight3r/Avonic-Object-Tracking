from threading import Event
from os import getenv
from dotenv import load_dotenv
from avonic_camera_api.camera_control_api import CameraAPI, converter, ResponseCode
import cv2
from avonic_camera_api.footage import FootageThread
from avonic_camera_api.camera_adapter import CameraSocket
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import MicrophoneSocket
from avonic_speaker_tracker.preset_model.PresetModel import PresetModel
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel
from avonic_speaker_tracker.audio_model.calibration import Calibration
import requests
from threading import Thread
from time import sleep

class GeneralController:
    def __init__(self):
        self.event = Event()
        self.info_threads_event = Event()
        self.footage_thread_event = Event()
        self.info_threads_break = Event() # THIS IS ONLY FOR DESTROYING THREADS
        self.info_threads_break.clear()
        self.thread = None
        self.url = '127.0.0.1:5000'
        self.cam_sock = None  # Only for testing
        self.cam_api = None
        self.mic_api = None
        self.secret = None
        self.ws = None
        self.preset_locations = None
        self.audio_model = None
        self.preset_model = None
        self.model = None
        self.camera_footage = None
        self.video = None
        self.thread_mic = None
        self.thread_cam = None
        self.preset = True

    def load_env(self):
        self.preset = True
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
        self.video = cv2.VideoCapture('rtsp://' + getenv("CAM_IP") + ':554/live/av0')
        self.footage_thread = FootageThread(self.video, self.footage_thread_event)
        self.footage_thread.start()

        # Initialize camera and microphone info threads
        self.info_threads_event.set()
        self.info_threads_break.clear() # THIS IS ONLY FOR DESTROYING THREADS
        self.thread_mic = Thread(target=self.send_update, args=(self.get_mic_info, '/update/microphone'))
        self.thread_cam = Thread(target=self.send_update, args=(self.get_cam_info, '/update/camera'))
        self.thread_mic.start()
        self.thread_cam.start()

    def __del__(self):
        self.preset = False
        self.footage_thread_event.set()
        self.info_threads_break.set()

        try:
            self.thread_mic.join()
        except:
            print("Trying to destruct None thread")
        try:
            self.thread_cam.join()
        except:
            print("Trying to destruct None thread")
        try:
            self.footage_thread.join()
        except:
            print("Trying to destruct None thread")
        try:
            cv2.destroyAllWindows()
        except:
            print("Trying to destruct None thread")
        try:
            self.video.release()
        except:
            print("Trying to destruct None thread")

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
        self.preset_locations = new_controller.preset_locations
        self.ws = new_controller.ws
        self.audio_model = AudioModel()
        self.preset_model = PresetModel()

    def set_mic_api(self, new_mic_api):
        self.mic_api = new_mic_api

    def set_cam_api(self, new_cam_api):
        self.cam_api = new_cam_api

    def get_model_based_on_choice(self):
        if self.preset:
            return self.preset_model
        return self.audio_model

    def set_preset_collection(self, new_preset_collection):
        self.preset_locations = new_preset_collection

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
            direction = [0, 0, 1]
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
            if self.info_threads_break.is_set():
                flag = False
            if not self.info_threads_event.is_set():
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
    integration_passed.footage_thread_event.set()
    integration_passed.info_threads_break.set()

    integration_passed.thread_mic.join()
    integration_passed.thread_cam.join()
    integration_passed.footage_thread.join()
    cv2.destroyAllWindows()
    integration_passed.video.release()
    raise SystemExit
