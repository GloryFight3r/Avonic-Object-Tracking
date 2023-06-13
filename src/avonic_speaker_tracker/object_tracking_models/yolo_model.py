import cv2
import numpy as np
from ultralytics import YOLO
import torch

class YOLOPredict:
    model:YOLO | None = None

    def __init__(self, path = "./src/object_tracker/"):
        self.model = YOLO("yolov8m.pt")

    def get_bounding_boxes_image(self, frame):
        results = self.model(frame, device="mps", classes=0)
        result = results[0]

        bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
        for x in bboxes:
            (x, y, x2, y2) = x
            self.draw_prediction(frame, "Person", x, y, x2, y2)

        return (frame, bboxes)

    def get_bounding_boxes(self, frame)->np.ndarray:
        results = self.model(frame, classes=0, device="mps")
        result = results[0]

        bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')

        return bboxes

    def draw_prediction(self, img, label, left, top, right, bottom):
        cv2.rectangle(img, (left, top), (right, bottom), [0, 0, 0], 2)
        cv2.putText(img, label, (left-10,top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 0], 2)
