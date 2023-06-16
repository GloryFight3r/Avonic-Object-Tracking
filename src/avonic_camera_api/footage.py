from threading import Thread
from multiprocessing import Value, Array
from ctypes import c_int
import base64
import cv2 # type: ignore
import numpy as np
import time
from avonic_camera_api.camera_control_api import CameraAPI

class FootageThread(Thread):
    buffer = Array('c', b'\0' * 1000000, lock=False)
    buflen = Value('i', 320000, lock=False)
    resolution = np.array([1920.0, 1080.0])

    def __init__(self, footage: cv2.VideoCapture, event: c_int):
        """ Constructor for the footage thread

            Params:
                footage: the footage stream from which to read frames
                event: the even that stops the thread when set to 0

        """
        super().__init__()
        self.footage = footage
        self.frame = None
        self.event = event
        self.show_bounding_boxes = False

    def run(self):
        while self.event.value != 0:
            success, self.frame = self.footage.read()

            if success:
                buffer = cv2.imencode('.jpg', self.frame)[1]
                self.buffer.raw = buffer
                self.buflen.value = len(buffer)
            time.sleep(0.1)
        print("Close footage thread")

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii

        Returns:
            Stringified base64 encoded frame
        """
        ret = str(base64.b64encode(self.buffer.raw[:self.buflen.value])
            , 'ascii')
        return ret
