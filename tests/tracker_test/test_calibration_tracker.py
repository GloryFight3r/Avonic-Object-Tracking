"""import pytest
import numpy as np
from unittest import mock

from avonic_speaker_tracker.object_model.ObjectModel import ObjectModel

def generate_box_lists():
    return [
        ([np.array([0, 0, 10, 10]), np.array([10, 10, 20, 20])],
         np.array([21, 20]), np.array([10, 10, 20, 20])),
        ([np.array([0, 0, 10, 10]), np.array([10, 10, 20, 20])],
         np.array([10, 20]), np.array([0, 0, 10, 10])),
        ([np.array([100, 10, 101, 101]), np.array([10, 10, 120, 220])],
         np.array([200, 400]), np.array([10, 10, 120, 220]))
    ]

@pytest.mark.parametrize("boxes, resolution, center", generate_box_lists())
def test_get_center_box(boxes, resolution, center):
    obj_model = ObjectModel(None, None, resolution)
    assert (obj_model.get_center_box(boxes) == center).all()

def test_calculate_speed():
    obj_model = ObjectModel(None, None, np.array([100, 80]))
    assert obj_model.calculate_speed(np.array([0, 0, 0])) == [20, 20]

def generate_box_with_movement():
    return [
            (np.array([0, 0, 10, 10]), np.array([10, 10]), (np.array([0, 0]), np.array([20, 20])))
    ]

@pytest.mark.parametrize("box, resolution, movement", generate_box_with_movement())
def test_get_movement_to_box(box, resolution, movement):
    cam_api = mock.Mock()
    cam_api.calculate_fov.return_value = 0
    obj_model = ObjectModel(cam_api, None, resolution)
    assert obj_model.get_movement_to_box(box) == movement
"""
