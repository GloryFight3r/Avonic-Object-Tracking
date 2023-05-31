from threading import Event
from os import getenv
import socket
from dotenv import load_dotenv
import cv2
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_adapter import Camera
from avonic_camera_api.footage import ObjectTrackingThread, FootageThread
from avonic_speaker_tracker.boxtracking import ThresholdBoxTracker
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import UDPSocket
from avonic_speaker_tracker.preset import PresetCollection
from avonic_speaker_tracker.calibration import Calibration
from object_tracker.yolo import Yolo
from object_tracker.yolov2 import YOLOPredict

import rtsp

class GeneralController():
    def __init__(self):
        self.event = Event()
        self.event2 = Event()
        self.object_tracking_event = Event()
        self.thread = None
        self.url = '127.0.0.1:5000'
        self.cam_api = None
        self.mic_api = None
        self.secret = None
        self.ws = None
        self.preset_locations = None
        self.calibration = None
        self.camera_footage = None
        self.box_tracker = None
        self.video = cv2.VideoCapture(
                'rtsp://' + getenv("CAM_IP") + ':554/live/av0'
        )
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    def load_env(self):
        url = getenv("SERVER_ADDRESS")
        if url is not None:
            self.url = url
        load_dotenv()
        cam_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cam_addr = (getenv("CAM_IP"), int(getenv("CAM_PORT")))
        self.cam_api = CameraAPI(Camera(cam_sock, cam_addr))
        mic_addr = (getenv("MIC_IP"), int(getenv("MIC_PORT")))
        mic_sock = UDPSocket(mic_addr)
        self.mic_api = MicrophoneAPI(mic_sock, int(getenv("MIC_THRESH")))
        self.preset_locations = PresetCollection()
        self.calibration = Calibration()
        self.secret = getenv("SECRET_KEY")

        self.box_tracker = ThresholdBoxTracker(self.cam_api, np.array([1920.0, 1080.0]), 5)
        self.footage_thread = FootageThread(self.video, self.event2)
        self.footage_thread.start()
        self.object_tracking_thread = ObjectTrackingThread(YOLOPredict(), self.box_tracker, self.footage_thread,
                                                        self.object_tracking_event)
        self.object_tracking_event.set()

    def __del__(self):
        self.video.release()
        self.object_tracking_event.set()

    def load_mock(self):
        self.cam_api = CameraAPI(None)
        self.mic_api = MicrophoneAPI(None, 55)
        self.calibration = Calibration()
        self.preset_locations = PresetCollection()

    def copy(self, new_controller):
        self.event = new_controller.event
        self.thread = new_controller.thread
        self.cam_api = new_controller.cam_api
        self.mic_api = new_controller.mic_api
        self.calibration = new_controller.calibration
        self.preset_locations = new_controller.preset_locations
        self.ws = new_controller.ws

    def set_mic_api(self, new_mic_api):
        self.mic_api = new_mic_api

    def set_cam_api(self, new_cam_api):
        self.cam_api = new_cam_api
