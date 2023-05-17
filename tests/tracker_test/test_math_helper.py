import pytest
from math import pi
import numpy as np

from avonic_speaker_tracker.math_helper import angle_between_vectors

def generate_vectors_angles():
    return [
        ([1, 1, 1], [2, 2, 2], 1),
        ([1, 0, 0], [0, 1, 1], np.cos(pi/2)),
        ([1, 0, 0], [1, 1, 0], np.cos(pi/4)),
    ]

@pytest.mark.parametrize("v1, v2, exp_angle", generate_vectors_angles())
def test_angle_between_vectors(v1, v2, exp_angle):
    angle = angle_between_vectors(np.array(v1), np.array(v2))
    # floats are not exactly the same in this case
    assert abs(angle - exp_angle) <= 1E-4
