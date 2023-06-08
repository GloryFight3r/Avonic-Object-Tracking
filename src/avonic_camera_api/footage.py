from threading import Thread
from multiprocessing import Value, Array
import base64
import time
import numpy as np
import cv2 # type: ignore

class FootageThread(Thread):
    buffer = Array('c', b'\0' * 1000000, lock=False)
    buflen = Value('i', 320000, lock=False)
    resolution = np.array([1920.0, 1080.0])

    def __init__(self, camera_footage: cv2.VideoCapture, event):
        """ Constructor for the footage thread

        Args:
            event (): event that stops the thread
            camera_footage: object to read from camera footage
        """
        super().__init__()
        self.camera_footage = camera_footage
        self.success = None
        self.frame = None
        self.event = event
        self.ret = None

    def run(self):
        """ Body of the thread that keeps receiving camera footage and loads it into the buffer """
        while not self.event.is_set():
            time.sleep(0.01)
            self.success, self.frame = self.camera_footage.read()  # read the camera frame
            if self.success:
                self.ret, buffer = cv2.imencode('.jpg', self.frame)
                string = base64.b64encode(buffer)
                length = len(string)
                self.buffer.raw = string
                self.buflen.value = length
            else:
                break

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii
        
        Returns:
            
        """

        return str(self.buffer.raw[:self.buflen.value], 'ascii')
