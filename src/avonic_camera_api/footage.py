import base64
import cv2
from threading import Thread
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI

from object_tracker.yolov2 import YOLOPredict
from avonic_speaker_tracker.calibration_tracker import CalibrationTracker

class ObjectTrackingThread(Thread):
    def __init__(self, nn: YOLOPredict, trck: CalibrationTracker, stream, event):
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
                self.stream.buffer = frame


class FootageThread(Thread):
    resolution:np.ndarray = np.array([])
    camera:CameraAPI | None = None
    frame = None
    buffer = None
    event = None
    show_bounding_boxes:bool | None = None

    def __init__(self, camera, event):
        super().__init__()
        self.camera = camera
        self.frame = None
        self.buffer = None
        self.event = event
        self.show_bounding_boxes = False

        # resolution of 
        self.resolution = np.array([1920.0, 1080.0])

    def run(self):
        while not self.event.is_set():
            ret, self.frame = self.camera.read()

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii

        Returns:

        """
        if self.show_bounding_boxes and self.buffer is not None:
            ret, jpg = cv2.imencode('.jpg', self.buffer)
            data = base64.b64encode(jpg).decode('ascii')

        else:
            ret, jpg = cv2.imencode('.jpg', self.frame)
            data = base64.b64encode(jpg).decode('ascii')
        return data
