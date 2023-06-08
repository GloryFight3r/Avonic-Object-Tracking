import pytest
import numpy as np

from avonic_speaker_tracker.boxtracking import BoxTracker
from avonic_camera_api.camera_control_api import CameraAPI

def generate_tests():
    return [
        ([40.0, 15.0], [0, 30, 20, 0], np.array([20, 20, (40.0 / 1920) * (-950), (15.0/1080) * (525)])),
        ([34.0, 15.0], [100, 30, 500, 0], np.array([20, 20, (34.0 / 1920) * (-660), (15.0/1080) * (525)])),
        ([43.0, 17.0], [3, 1000, 20, 950], np.array([20, 20, (43.0 / 1920) * (-960 + (23/2)), (17.0/1080) * (540 - (1950/2))]))
    ]

@pytest.fixture
def box_tracker():
    cam_api = CameraAPI(None)
    resolution = np.array([1920.0, 1080.0])
    return BoxTracker(cam_api, resolution)

@pytest.mark.parametrize("fov, bbox, expected", generate_tests())
def test_camera_track(box_tracker, fov, bbox, expected, monkeypatch):
    def mocked_move(speed_one, speed_two, alpha, beta):
        assert np.array_equal(np.array([speed_one, speed_two, alpha, beta]), expected)
    def mocked_fov():
        return fov

    monkeypatch.setattr(box_tracker.cam, "move_relative", mocked_move)
    monkeypatch.setattr(box_tracker.cam, "calculate_fov", mocked_fov)

    box_tracker.camera_track(bbox)

def generate_errors():
    return [
        ([40.0, 15.0], [-1, 30, 20, 0]),
        ([34.0, 15.0], [100, 30, 1921, 0]),
        ([43.0, 17.0], [3, -1, 20, 0]),
        ([43.0, 17.0], [3, 40, -1, 0]),
        ([43.0, 17.0], [3, 40, 10, -1])
    ]


@pytest.mark.parametrize("fov, bbox", generate_errors())
def test_camera_assertions(box_tracker, fov, bbox, monkeypatch):
    def mocked_move(speed_one, speed_two, alpha, beta):
        pass
    def mocked_fov():
        return fov

    monkeypatch.setattr(box_tracker.cam, "move_relative", mocked_move)
    monkeypatch.setattr(box_tracker.cam, "calculate_fov", mocked_fov)

    with pytest.raises(AssertionError):
        box_tracker.camera_track(bbox)
