from threading import Thread
import base64
import time
import cv2

class FootageThread(Thread):
    def __init__(self, url:str, camera_footage: cv2.VideoCapture, event):
        super().__init__()
        #self.event = event
        self.camera_footage = camera_footage
        self.success = None
        self.frame = None
        self.url = "http://" + url
        self.event = event
        self.ret = None
        self.buffer = None

    def run(self):
        while not self.event.is_set():
            time.sleep(0.01)
            self.success, self.frame = self.camera_footage.read()  # read the camera frame
            if self.success:
                self.ret, self.buffer = cv2.imencode('.jpg', self.frame)
            else:
                break

    def get_frame(self):
        data = base64.b64encode(self.buffer).decode('ascii')
        return data
