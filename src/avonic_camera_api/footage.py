from threading import Thread
import base64
import time
import cv2
from threading import Thread
import cv2
import base64
import copy
import time
from avonic_speaker_tracker.boxtracking import BoxTracker
from object_tracker.yolov2 import YOLOPredict

class ObjectTrackingThread(Thread):
    def __init__(self, nn: YOLOPredict, trck: BoxTracker, stream, event):
        super().__init__()
        self.stream = stream
        # the neural network
        self.nn = nn
        self.trck = trck
        self.event = event

    def run(self):
        while not self.event.is_set():
            frame = self.stream.frame  # read the camera frame
            if frame is not None:
                boxes = self.nn.get_bounding_boxes(frame)
                if len(boxes) > 0:
                    last_box = copy.deepcopy(boxes)
                    try:
                        self.trck.camera_track(boxes[0][0])
                    except:
                        last_box = [[last_box]]
                        self.trck.camera_track(boxes)
                else:
                    last_box = []

                for bb in last_box:
                    print(bb[0])
                    (x, y, x2, y2) = bb[0]
                    self.nn.draw_prediction(frame, "person", x, y, x2, y2)
                self.stream.buffer = frame


class FootageThread(Thread):
    def __init__(self, camera, event):
        super().__init__()
        self.camera = camera
        self.frame = None
        self.buffer = None
        self.event = event
        self.show_bounding_boxes = False

    def run(self):
        while not self.event.is_set():
            ret, self.frame = self.camera.read()

    def get_frame(self):
        if self.show_bounding_boxes and self.buffer is not None:
            ret, jpg = cv2.imencode('.jpg', self.buffer)
            data = base64.b64encode(jpg).decode('ascii')

        else:
            ret, jpg = cv2.imencode('.jpg', self.frame)
            data = base64.b64encode(jpg).decode('ascii')

        return data
