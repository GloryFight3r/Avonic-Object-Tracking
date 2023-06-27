from unittest import mock
from ultralytics import YOLO
import torch
import cv2
import numpy as np

from maat_tracking.object_model.yolov8 import YOLOPredict


class MockedBoxes:
    def __init__(self):
        self.conf = mock.Mock()
        self.conf.cpu.return_value = torch.tensor([1, 3, 5, 1, 3, 4])
        self.cls = mock.Mock()
        self.cls.cpu.return_value = torch.tensor([0, 4, 0, 3, 1, 2])
        self.xyxy = mock.Mock()
        boxes = [[0, 0, 1, 1], [1, 2, 3, 4],
                 [3, 3, 5, 5], [1, 9, 2, 8],
                 [1, 5, 2, 7], [0, 8, 8, 9]]

        # self.xyxy.cpu.return_value = torch.tensor([torch.tensor(box) for box in boxes])
        self.xyxy.cpu.return_value = torch.tensor(boxes)


class MockedResult:
    def __init__(self):
        self.boxes = MockedBoxes()


def test_get_bounding_boxes(monkeypatch):
    def mocked_init(self, path):
        pass

    def mocked_predict(frame, classes, device):
        return [MockedResult()]

    monkeypatch.setattr(YOLO, "__init__", mocked_init)
    yolo = YOLOPredict()

    monkeypatch.setattr(yolo.model, "predict", mocked_predict)

    ret = yolo.get_bounding_boxes(frame=None)
    print(ret)
    assert (np.array(ret) == np.array([np.array([0, 0, 1, 1]), np.array([3, 3, 5, 5])])).all()


def test_draw_prediction(monkeypatch):
    rect_calls = []
    text_calls = []

    def mocked_init(self, path):
        pass

    def mocked_rectangle(im, lt, rb, color, b):
        rect_calls.append("Called")

    def mocked_put_text(im, label, lt, font, a, color, b):
        text_calls.append("Called")

    monkeypatch.setattr(YOLO, "__init__", mocked_init)
    monkeypatch.setattr(cv2, "rectangle", mocked_rectangle)
    monkeypatch.setattr(cv2, "putText", mocked_put_text)
    yolo = YOLOPredict()
    yolo.draw_prediction(None, None, 10, 10, None, None)
    assert len(rect_calls) == len(text_calls) == 1
