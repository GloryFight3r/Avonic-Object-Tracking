import cv2
import numpy as np
from ultralytics import YOLO
import torch

class YOLOPredict:
    def __init__(self, conf_level = 0.0):
        self.model = YOLO("yolov8m.pt")

        # change conf_level to a higher number to filter low confidence boxes
        self.conf_level = conf_level

    def get_bounding_boxes(self, frame):
        results = self.model.predict(frame, classes=0, device="cpu")
        result = results[0]

        print("START!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        person_indices = set(torch.nonzero(result.boxes.cls.cpu() == 0))

        bboxes = np.array(result.boxes.xyxy.cpu(), dtype='int')
        persons = []
        for index in person_indices:
            persons.append(bboxes[index])

        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        print(persons)
        return persons

    def draw_prediction(self, img, label, left, top, right, bottom):
        cv2.rectangle(img, (left, top), (right, bottom), [0, 0, 0], 2)
        cv2.putText(img, label, (left-10,top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [0, 0, 0], 2)
