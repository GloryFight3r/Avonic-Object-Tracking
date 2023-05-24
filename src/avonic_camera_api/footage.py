from time import sleep
from threading import Thread
import asyncio
import cv2
import base64
import time

from object_tracker.yolo import Yolo

class FootageThread(Thread):
    def __init__(self, url:str, camera_footage: cv2.VideoCapture, nn: Yolo):
        super().__init__()
        #self.event = event
        self.camera_footage = camera_footage
        self.success = None
        self.frame = None
        self.url = "http://" + url

        # the neural network
        self.nn = nn

    def run(self):
        while True:
            time.sleep(0.01)
            self.success, self.frame = self.camera_footage.read()  # read the camera frame
            if not self.success:
                break
            else:
                test = self.process(self.frame)
                self.ret, self.buffer = cv2.imencode('.jpg', self.frame)

    def get_frame(self):
        data = base64.b64encode(self.buffer).decode('ascii')  # concat frame one by one and show result
        return data

    def process(self, frame):
        new_frame = self.nn.get_bounding_boxes(frame)
        return new_frame
