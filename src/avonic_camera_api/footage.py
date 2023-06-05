from threading import Thread
from multiprocessing import Value, Array
import base64
import time
import cv2
from threading import Thread
import cv2
import base64
import copy
import time
from object_tracker.yolov2 import YOLOPredict
from avonic_speaker_tracker.calibration_tracker import CalibrationTracker

class ObjectTrackingThread(Thread):
    def __init__(self, nn: YOLOPredict, trck: CalibrationTracker, stream, event):
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

    def run(self):
        """ Body of the thread that keeps receiving camera footage and loads it into the buffer """
        while not self.event.is_set():
            frame = self.stream.frame  # read the camera frame
            if frame is not None:
                boxes = self.nn.get_bounding_boxes(frame)
                if len(boxes) > 0:
                    last_box = self.trck.get_center_box(boxes)
                    self.trck.track_object(last_box)
                else:
                    last_box = []
                (x, y, x2, y2) = last_box
                self.nn.draw_prediction(frame, "person", x, y, x2, y2)
                #self.stream.buffer = frame


class FootageThread(Thread):
    buffer = Array('c', b'\0' * 1000000, lock=False)
    buflen = Value('i', 320000, lock=False)

    def __init__(self, camera, event):
        super().__init__()
        self.camera = camera
        self.frame = None
        self.event = event
        self.show_bounding_boxes = False

    def run(self):
        while not self.event.is_set():
            ret, self.frame = self.camera.read()
            if ret:
                ret, buffer = cv2.imencode('.jpg', self.frame)
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
