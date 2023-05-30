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

class FootageThread(Thread):
    def __init__(self, url:str, camera_footage: cv2.VideoCapture, nn: YOLOPredict, event, trck:BoxTracker):
        super().__init__()
        #self.event = event
        self.camera_footage = camera_footage
        self.success = None
        self.frame = None
        self.url = "http://" + url
        self.event = event
        self.ret = None
        self.buffer = None
        # the neural network
        self.nn = nn
        self.last_box = None
        self.trck = trck

    def run(self):
        k = 0
        while not self.event.is_set():
            time.sleep(0.01)
            self.success, self.frame = self.camera_footage.read()  # read the camera frame
            if self.success:
                
                if (k % 100 == 0):
                    #print("AS")
                    boxes = self.nn.get_bounding_boxes(self.frame)
                    if len(boxes) > 0:
                        self.last_box = copy.deepcopy(boxes)
                        self.trck.camera_track(boxes[0])
                    else:
                        self.last_box = None

                for bb in self.last_box:
                    (x, y, x2, y2) = bb
                    self.nn.draw_prediction(self.frame, "person", x, y, x2, y2)
                self.ret, self.buffer = cv2.imencode('.jpg', self.frame) #self.nn.get_bounding_boxes_image(self.frame))
                
                #box = self.nn.get_bounding_boxes_image(self.frame)
                #if(len(box) > 0):
                #    self.trck.camera_track(box[0])
                #print(self.buffer.shape)
            else:
                break
            k += 1

    def get_frame(self):

        data = base64.b64encode(self.buffer).decode('ascii')
        return data

    def process(self, frame):
        t = time.time()
        boxes = self.nn.get_bounding_boxes(frame)
        print(time.time() - t)
        # TO-DO
        # choose box closest to center
        # move camera to center on this box

         
