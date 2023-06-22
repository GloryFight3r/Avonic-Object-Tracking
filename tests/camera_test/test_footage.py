from multiprocessing import Value
import pytest
import numpy as np
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
    mocked_box_tracker = MockedBoxTracker()
    mocked_yolo = MockedYoloPredict()
    event = Value("i", 1, lock=False)
    thread = FootageThread(mocked_cam_footage, event, np.array([1920.0, 1080.0]))

    return thread

"""def test_run(footage_thread, monkeypatch):
    def mocked_imencode(tp, frame):
        assert frame == "mocked return"
        footage_thread.event.value = 0
        return (True, b'FEEB')

    monkeypatch.setattr(cv2, "imencode", mocked_imencode)
    footage_thread.run()

    assert footage_thread.get_frame() == base64.b64encode(b'FEEB').decode('ascii')
"""
