import pytest
import numpy as np
from unittest import mock

from avonic_speaker_tracker.object_model.ObjectModel import ObjectModel

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
    obj_model = ObjectModel(None, None, None, resolution)
    assert (obj_model.get_center_box(boxes) == center).all()

def test_calculate_speed():
    obj_model = ObjectModel(None, None, None, np.array([100, 80]))
    assert obj_model.calculate_speed(np.array([0, 0, 0])) == [20, 20]

def generate_box_with_movement():
    return [
            (np.array([0, 0, 10, 10]), np.array([10, 10]), (np.array([20, 20]), np.array([0, 0]))),
            (np.array([5, 5, 10, 10]), np.array([10, 10]), (np.array([20, 20]), np.array([0, 0])))
    ]

@pytest.mark.parametrize("box, resolution, movement", generate_box_with_movement())
def test_get_movement_to_box(box, resolution, movement):
    cam_api = mock.Mock()
    cam_api.calculate_fov.return_value = 0
    obj_model = ObjectModel(cam_api, None, None, resolution)
    res = obj_model.get_movement_to_box(box)
    print(res)
    assert (res[0] == movement[0]).all()
    assert (res[1] == movement[1]).all()
