from threading import Thread
from multiprocessing import Value, Array
from ctypes import c_int
import base64
import copy
import numpy as np
import cv2 # type: ignore

class FootageThread(Thread):
    buffer = Array('c', b'\0' * 1000000, lock=False)
    buflen = Value('i', 320000, lock=False)

    def __init__(self, footage: cv2.VideoCapture, event: c_int, resolution:np.ndarray):
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
        self.resolution = resolution

        self.box_frame = None
        self.bbxes = np.array([])
        self.pixel:np.ndarray | None = None
        self.focused_box:np.ndarray | None = None

    def run(self):
        while self.event.value != 0:
            success, self.frame = self.footage.read()

            if success:
                buffer = cv2.imencode('.jpg', self.frame)[1]
                self.buffer.raw = buffer
                self.buflen.value = len(buffer)
        print("Close footage thread")

    def set_bbxes(self, bbxes):
        self.bbxes = bbxes

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii

        Returns:
            Stringified base64 encoded frame
        """
        #if self.box_frame is not None:
        #    return str(base64.b64encode(self.box_frame), 'ascii')
        #self.draw_bb()
        return str(base64.b64encode(self.buffer.raw[:self.buflen.value])
            , 'ascii')

    def draw_bb(self):
        cur_frame = copy.deepcopy(self.frame)
        for box in self.bbxes:
            (x, y, x2, y2) = box
            self.draw_prediction(cur_frame, "person", x, y, x2, y2, [0, 0, 0])
        if self.pixel is not None:
            print(self.pixel)
            self.draw_prediction(cur_frame, "pixel", self.pixel[0], self.pixel[1], self.pixel[0], self.pixel[1], [255, 0, 0])
        if self.focused_box is not None:
            (x, y, x2, y2) = self.focused_box
            self.draw_prediction(cur_frame, "person", x, y, x2, y2, [0, 0, 255])

        buffer = cv2.imencode('.jpg', cur_frame)[1]
        self.buffer.raw = buffer
        self.buflen.value = len(buffer)

    def draw_prediction(self, img, label, left, top, right, bottom, clr):
        cv2.rectangle(img, (left, top), (right, bottom), clr, 2)
        cv2.putText(img, label, (left-10,top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, clr, 2)
    
