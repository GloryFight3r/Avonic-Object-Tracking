import cv2
import numpy as np
from ultralytics import YOLO
import torch

class YOLOPredict:
    model = None

    def __init__(self):
        self.model = YOLO("yolov8m.pt")

    def get_bounding_boxes_image(self, frame):
        results = self.model(frame, device="mps", classes=0)
        result = results[0]

        bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
        for x in bboxes:
            (x, y, x2, y2) = x
            self.draw_prediction(frame, "Person", x, y, x2, y2)

        return frame

    def get_bounding_boxes(self, frame):
        results = self.model.predict(frame, classes=0, device="cpu")
        result = results[0]
        conf_indices = set(torch.nonzero(result.boxes.conf.cpu() > 0.0))
        person_indices = set(torch.nonzero(result.boxes.cls.cpu() == 0))

        bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
        persons = []
        for index in person_indices:
            persons.append(bboxes[index])

        return persons

    def draw_prediction(self, img, label, left, top, right, bottom):
        cv2.rectangle(img, (left, top), (right, bottom), [0, 0, 0], 2)
        cv2.putText(img, label, (left-10,top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 0], 2)
