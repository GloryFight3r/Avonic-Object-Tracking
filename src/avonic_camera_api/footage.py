from threading import Thread
from multiprocessing import Value, Array
import base64
import time
import numpy as np
import cv2 # type: ignore

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
        while self.event.value != 0:
            success, self.frame = self.camera.read()

            if success:
                buffer = cv2.imencode('.jpg', self.frame)[1]
                self.buffer.raw = buffer
                self.buflen.value = len(buffer)
        print("Close footage thread")

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii

        Returns:
            Stringified base64 encoded frame
        """
        ret = str(base64.b64encode(self.buffer.raw[:self.buflen.value])
            , 'ascii')
        return ret
