import pytest
import numpy as np

from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.footage import FootageThread
from avonic_speaker_tracker.object_model.ObjectModel import ObjectModel

def generate_tests():
    return [
        ([40.0, 15.0], [0, 0, 20, 30],
         np.array([20, 20, (40.0 / 1920) * (-950), (15.0/1080) * (525)])),
        ([34.0, 15.0], [100, 0, 500, 50],
         np.array([20, 20, (34.0 / 1920) * (-660), (15.0/1080) * (525)])),
        ([43.0, 17.0], [3, 950, 20, 1000],
         np.array([20, 20, (43.0 / 1920) * (-960 + (23/2)), (17.0/1080) * (540 - (1950/2))]))
]

@pytest.fixture
def obj_model():
    cam_api = CameraAPI(None, None)
    mic_api = MicrophoneAPI(None)
    stream = FootageThread(None, None, np.array([1920.0, 1080.0]), None)

    obj_model = ObjectModel(cam_api, mic_api, stream, None, np.array([1920.0, 1080.0]))

    return obj_model

@pytest.mark.parametrize("fov, bbox, expected", generate_tests())
def test_camera_track(obj_model, fov, bbox, expected, monkeypatch):
    def mocked_move(speed_one, speed_two, alpha, beta):
        assert np.array_equal(np.array([speed_one, speed_two, alpha, beta]), expected)
    def mocked_fov():
        return fov

    monkeypatch.setattr(obj_model.cam_api, "move_relative", mocked_move)
    monkeypatch.setattr(obj_model.cam_api, "calculate_fov", mocked_fov)

    obj_model.get_movement_to_box(bbox)

def generate_errors():
    return [
        ([40.0, 15.0], [-1, 30, 20, 0]),
        ([34.0, 15.0], [100, 30, 1921, 0]),
        ([43.0, 17.0], [3, -1, 20, 0]),
        ([43.0, 17.0], [3, 40, -1, 0]),
        ([43.0, 17.0], [3, 40, 10, -1])
    ]


@pytest.mark.parametrize("fov, bbox", generate_errors())
def test_camera_assertions(obj_model, fov, bbox, monkeypatch):
    def mocked_move(speed_one, speed_two, alpha, beta):
        pass
    def mocked_fov():
        return fov

    monkeypatch.setattr(obj_model.cam_api, "move_relative", mocked_move)
    monkeypatch.setattr(obj_model.cam_api, "calculate_fov", mocked_fov)

    with pytest.raises(AssertionError):
        obj_model.get_movement_to_box(bbox)
