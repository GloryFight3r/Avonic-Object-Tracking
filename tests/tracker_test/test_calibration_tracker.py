import pytest
import numpy as np

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
    cal_track = ObjectModel(None, None, resolution)
    assert (cal_track.get_center_box(boxes) == center).all()
