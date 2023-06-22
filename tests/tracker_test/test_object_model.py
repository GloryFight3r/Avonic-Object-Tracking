from unittest import mock
import pytest
import numpy as np
import cv2

from avonic_speaker_tracker.object_model.ObjectModel import ObjectModel
from avonic_speaker_tracker.object_model.model_two.WaitObjectAudioModel import WaitObjectAudioModel

def generate_box_lists():
    return [
        ([np.array([0, 0, 10, 10]), np.array([10, 10, 20, 20]), np.array([1000, 1000, 2000, 2000])],
         np.array([21.0, 20.0]), np.array([10, 10, 20, 20])),
        ([np.array([0, 0, 10, 10]), np.array([10, 10, 20, 20])],
         np.array([10, 20]), np.array([0, 0, 10, 10])),
        ([np.array([0, 10, 100, 100]), np.array([110, 10, 120, 220])],
         np.array([200, 400]), np.array([110, 10, 120, 220]))
    ]

@pytest.mark.parametrize("boxes, resolution, center", generate_box_lists())
def test_get_center_box(boxes, resolution, center):
    obj_model = ObjectModel(None, None, None, None, resolution)
    assert (obj_model.get_center_box(boxes) == center).all()

def test_calculate_speed():
    obj_model = ObjectModel(None, None, None, None, np.array([100, 80]))
    assert (obj_model.calculate_speed(np.array([0, 0])) == [13, 11]).all()

def generate_box_with_movement():
    return [
            (np.array([0, 0, 10, 10]), np.array([10, 10]),
                (np.array([13, 12]), np.array([0, -25]))),
            (np.array([5, 5, 10, 10]), np.array([10, 10]),
                (np.array([13, 13]), np.array([25, -37.5])))
    ]

@pytest.mark.parametrize("box, resolution, movement", generate_box_with_movement())
def test_get_movement_to_box(box, resolution, movement):
    cam_api = mock.Mock()
    cam_api.calculate_fov.return_value = 100
    obj_model = ObjectModel(cam_api, None, None, None, resolution)
    res = obj_model.get_movement_to_box(box)
    assert np.allclose(res[0], movement[0])
    assert np.allclose(res[1], movement[1])


class MockedCamAPI:
    def __init__(self):
        pass

    def move_relative(self, s1, s2, a1, a2):
        return 50

    def move_absolute(self, s1, s2, a1, a2):
        pass

    def calculate_fov(self):
        return 100

    def direct_zoom(self, value):
        pass

class MockedMicAPI:
    def __init__(self):
        pass

    def get_direction(self):
        return np.array([3, 2, 1])

class MockedMicAPIWrongDirection:
    def __init__(self):
        pass

    def get_direction(self):
        return ""


def test_track_object(monkeypatch):
    nn = mock.Mock()
    nn.get_bounding_boxes.return_value = [np.array([0, 0, 10, 10])]
    monkeypatch.setattr(np, "frombuffer", lambda bts, tp: np.array([0, 0, 0, 0]))
    monkeypatch.setattr(cv2, "imdecode", lambda im, tp: np.array([0, 0, 0, 0]))

    stream = mock.Mock()
    stream.buffer.raw = [0, 1]
    stream.buflen.value = 1
    object_audio_model = WaitObjectAudioModel(MockedCamAPI(),
                                              None, np.array([100, 100]), 0,
                                              nn, stream)
    object_audio_model.sleep()
    object_audio_model.is_object_tracking = True
    object_audio_model.object_tracking_counter = 40
    object_audio_model.track_object()
    object_audio_model2 = WaitObjectAudioModel(MockedCamAPI(),
                                               None, np.array([100, 100]), 100,
                                               nn, stream)
    object_audio_model2.is_object_tracking = True
    object_audio_model2.object_tracking_counter = 40
    object_audio_model2.track_object()

def test_point(monkeypatch):
    object_audio_model = WaitObjectAudioModel(MockedCamAPI(), MockedMicAPI(),
                                              np.array([100, 100]), 0,
                                              None, None)
    monkeypatch.setattr(object_audio_model.calibration, "mic_to_cam", np.array([1, 2, 3]))
    monkeypatch.setattr(object_audio_model.calibration, "mic_height", 1.5)
    object_audio_model.point()
    assert (object_audio_model.prev_dir == np.array([139, -35, 9715])).all()

def test_point_zoom(monkeypatch):
    object_audio_model = WaitObjectAudioModel(MockedCamAPI(), MockedMicAPI(),
                                              np.array([100, 100]), 0,
                                              None, None)
    monkeypatch.setattr(object_audio_model.calibration, "mic_to_cam", np.array([1, 2, 3]))
    monkeypatch.setattr(object_audio_model.calibration, "mic_height", 1.5)
    object_audio_model.speak_delay = 100
    assert not object_audio_model.point()

def test_point_wrong_direction():
    object_audio_model = WaitObjectAudioModel(MockedCamAPI(),
                                              MockedMicAPIWrongDirection(),
                                              np.array([100, 100]), 0,
                                              None, None)
    assert not object_audio_model.point()
    assert (object_audio_model.prev_dir == np.array([0, 0, 1])).all()
