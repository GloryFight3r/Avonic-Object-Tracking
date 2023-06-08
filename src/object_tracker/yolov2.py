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

        return (frame, bboxes)

    def get_bounding_boxes(self, frame)->np.ndarray:
        print("START")
        results = self.model(frame, classes=0, device="mps")
        result = results[0]
        #person_indices = torch.nonzero(result.boxes.cls.cpu() == 0)
        #persons = [result.boxes.cls.cpu()[i] for i in person_indices]

        bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
        print("DONE")
        #persons = []
        #for index in person_indices:
        #    persons.append(bboxes[index])

        return bboxes

