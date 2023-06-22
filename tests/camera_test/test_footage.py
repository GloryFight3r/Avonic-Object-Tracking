from multiprocessing import Value
import numpy as np
import pytest
from avonic_camera_api.footage import FootageThread

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
    event = Value("i", 1, lock=False)
    thread = FootageThread(mocked_cam_footage, event, np.array([1920.0, 1080.0]))

    return thread
