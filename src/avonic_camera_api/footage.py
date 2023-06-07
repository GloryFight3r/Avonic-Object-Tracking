from threading import Thread
from multiprocessing import Value, Array
import base64
import time
from threading import Thread
import cv2
import base64
import copy
import time
import numpy as np

class FootageThread(Thread):
    buffer = Array('c', b'\0' * 1000000, lock=False)
    buflen = Value('i', 320000, lock=False)
    box_frame = None

    def __init__(self, camera, event):
        super().__init__()
        self.camera = camera
        self.frame = None
        self.event = event
        self.show_bounding_boxes = False

    def run(self):
        while not self.event.is_set():
            success, self.frame = self.camera.read()

            if success:
                ret, buffer = cv2.imencode('.jpg', self.frame)
                self.buffer.raw = buffer
                self.buflen.value = len(buffer)
            #string = base64.b64encode(buffer)
            #length = len(string)
            #self.buffer.raw = string
            #self.buflen.value = length

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii

        Returns:

        """
        if self.box_frame is not None:
            return str(base64.b64encode(self.box_frame), 'ascii')
        return str(base64.b64encode(self.buffer.raw[:self.buflen.value])
            , 'ascii')
