from threading import Event
from os import getenv
from dotenv import load_dotenv
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_adapter import CameraSocket
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import MicrophoneSocket
from avonic_speaker_tracker.preset import PresetCollection
from avonic_speaker_tracker.calibration import Calibration


class GeneralController:
    def __init__(self):
        self.event = Event()
        self.thread = None
        self.url = '127.0.0.1:5000'
        self.cam_sock = None  # Only for testing
        self.cam_api = None
        self.mic_api = None
        self.secret = None
        self.ws = None
        self.preset_locations = None
        self.calibration = None

    def load_env(self):
        url = getenv("SERVER_ADDRESS")
        if url is not None:
            self.url = url
        load_dotenv()
        cam_addr = (getenv("CAM_IP"), int(getenv("CAM_PORT")))
        verify_address(cam_addr)
        self.cam_api = CameraAPI(CameraSocket(address=cam_addr))
        mic_addr = (getenv("MIC_IP"), int(getenv("MIC_PORT")))
        verify_address(mic_addr)
        self.mic_api = MicrophoneAPI(MicrophoneSocket(address=mic_addr), int(getenv("MIC_THRESH")))
        self.preset_locations = PresetCollection()
        self.calibration = Calibration()
        self.secret = getenv("SECRET_KEY")

    def load_mock(self):
        cam_addr = ('0.0.0.0', 52381)
        mic_addr = ('0.0.0.0', 45)
        self.cam_api = CameraAPI(CameraSocket(sock=self.cam_sock, address=cam_addr))
        self.mic_api = MicrophoneAPI(MicrophoneSocket(address=mic_addr), 55)
        self.calibration = Calibration()

    def copy(self, new_controller):
        self.event = new_controller.event
        self.thread = new_controller.thread
        self.cam_api = new_controller.cam_api
        self.mic_api = new_controller.mic_api
        self.calibration = new_controller.calibration

    def set_mic_api(self, new_mic_api):
        self.mic_api = new_mic_api

    def set_cam_api(self, new_cam_api):
        self.cam_api = new_cam_api


def verify_address(address):
    try:
        assert 0 <= address[1] <= 65535
        assert 0 <= int(address[0].split(".")[0]) <= 255 and \
               0 <= int(address[0].split(".")[1]) <= 255 and \
               0 <= int(address[0].split(".")[2]) <= 255 and \
               0 <= int(address[0].split(".")[3]) <= 255
    except AssertionError:
        print("ERROR: Address " + address + " is invalid!")
