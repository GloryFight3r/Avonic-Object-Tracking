import numpy as np
import pytest
from avonic_camera_api.converter import angle_vector, vector_angle


def test_angle_vector_basic():
    alpha = 0
    beta = 0
    assert angle_vector(alpha, beta) == [0.0, 0.0, 1.0]


def test_angle_vector_complex():
    alpha = -30
    beta = 60
    assert angle_vector(alpha, beta) == [-0.25, np.sqrt(3) / 4, np.sqrt(3) / 2]


def test_vector_angle_basic():
    assert vector_angle([0.0, 0.0, 1.0]) == (0, 0)


def test_vector_angle_complex():
    """ not normalised, length of vector is 2 """
    assert vector_angle([-0.5, np.sqrt(3), np.sqrt(3)]) == (-30, 60)


def test_vector_angle_invalid():
    with pytest.raises(Exception):
        vector_angle([0.0, 0.0, 0.0])
