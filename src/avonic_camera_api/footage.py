from threading import Thread
from multiprocessing import Array, Value
import base64
import numpy as np
import time
import cv2


class FootageThread(Thread):
    buffer = Array('b', range(320000), lock=False)
    buflen = Value('i', 320000)

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
            time.sleep(0.1)
            self.success, self.frame = self.camera_footage.read()  # read the camera frame
            if self.success:
                self.ret, buffer = cv2.imencode('.jpg', self.frame)
                self.buflen.value = len(buffer)
                self.buffer[:self.buflen.value] = np.frombuffer(buffer)
                print(self.buffer[5000], self.buflen.value)
            else:
                break

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii
        
        Returns:
            
        """
        print("gugug", self.buffer[5000], self.buflen.value)
        buffer = np.array(self.buffer[:self.buflen.value]).tobytes()
        data = base64.b64encode(buffer).decode('ascii')
        print(data[5])
        return data
