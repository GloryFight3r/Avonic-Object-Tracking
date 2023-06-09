from threading import Thread
from multiprocessing import Value, Array
import base64
import time
from threading import Thread
import base64
import copy
import time
import numpy as np
import cv2 # type: ignore

from object_tracker.yolov2 import YOLOPredict
from avonic_speaker_tracker.object_model.ObjectModel import ObjectModel

class ObjectTrackingThread(Thread):
    def __init__(self, nn: YOLOPredict, trck: ObjectModel, stream, event):
        """ Constructor for the footage thread

        Args:
            event (): event that stops the thread
            camera_footage: object to read from camera footage
        """
        super().__init__()
        self.stream = stream
        # the neural network
        self.nn = nn
        self.trck = trck
        self.event = event
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('output.avi', fourcc, 2.0, (1920, 1080))

    def run(self):
        """ Body of the thread that keeps receiving camera footage and loads it into the buffer """
        while self.event.value != 0:
            if self.event.value != 1:
                im_arr = np.frombuffer(self.stream.buffer.raw[:self.stream.buflen.value], np.byte)
                frame = cv2.imdecode(im_arr, cv2.IMREAD_COLOR)  # read the camera frame
                if frame is not None:
                    boxes = self.nn.get_bounding_boxes(frame)
                    if len(boxes) > 0:
                        last_box = self.trck.get_center_box(boxes)
                        self.trck.track_object(last_box)

                        # this won't work in production. It is purely for debugging purposes
                        #if True:
                        #    (x, y, x2, y2) = last_box
                        #    self.nn.draw_prediction(frame, "person", x, y, x2, y2)
                        #    self.stream.box_frame = cv2.imencode('.jpg', frame)[1]
                    # to write results to video
                    #self.out.write(frame)
                time.sleep(2)


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

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii

        Returns:

        """
        ret = str(base64.b64encode(self.buffer.raw[:self.buflen.value])
            , 'ascii')
        return ret
