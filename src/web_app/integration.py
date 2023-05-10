from threading import Event
from os import getenv
import socket
from dotenv import load_dotenv
from flask import Flask, jsonify, abort, render_template, make_response

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_adapter import Camera
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import UDPSocket

class GeneralController():
    def __init__(self):
        self.event = Event()
        self.thread = None
    
    def load_env(self):
        load_dotenv()
        cam_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cam_addr = (getenv("CAM_IP"), int(getenv("CAM_PORT")))
        self.cam_api = CameraAPI(Camera(cam_sock, cam_addr))
        mic_addr = (getenv("MIC_IP"), int(getenv("MIC_PORT")))
        mic_sock = UDPSocket(mic_addr)
        self.mic_api = MicrophoneAPI(mic_sock, int(getenv("MIC_THRESH")))
    
    def load_mock(self):
        self.cam_api = CameraAPI(None)
        self.mic_api = MicrophoneAPI(None, 55)
    
    def copy(self, new_controller):
        self.event = new_controller.event
        self.thread = new_controller.thread
        self.cam_api = new_controller.cam_api
        self.mic_api = new_controller.mic_api

    def set_mic_api(self, new_mic_api):
        self.mic_api = new_mic_api
    
    def set_cam_api(self, new_cam_api):
        self.cam_api = new_cam_api
