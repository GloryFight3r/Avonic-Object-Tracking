import base64
from threading import Event
import pytest
import cv2
from avonic_camera_api.footage import FootageThread
from object_tracker.yolov2 import YOLOPredict

class MockedCv:
    def __init__(self):
        pass
    def read(self):
        return (True, "mocked return")

class MockedBoxTracker:
    def __init__(self):
        pass
    def camera_track(self, bx):
        pass

class MockedYoloPredict:
    def __init__(self):
        pass

    def get_bounding_boxes(self, frame):
        return [[0, 0, 0, 0]]
    def get_bounding_boxes_image(self, frame):
        pass
    def draw_prediction(self, img, lbl, x, y, x2, y2):
        pass

@pytest.fixture
def footage_thread():
    mocked_cam_footage = MockedCv()
    event = Event()
    thread = FootageThread(mocked_cam_footage, event)

    return thread

def test_run(footage_thread, monkeypatch):
    def mocked_imencode(tp, frame):
        assert frame == "mocked return"
        footage_thread.event.set()
        return (True, b'FEEB')

    monkeypatch.setattr(cv2, "imencode", mocked_imencode)
    footage_thread.run()

    assert footage_thread.get_frame() == base64.b64encode(b'FEEB').decode('ascii')
