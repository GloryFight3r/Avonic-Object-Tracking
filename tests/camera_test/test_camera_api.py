import numpy as np
import pytest
from avonic_camera_api.converter import angle_vector, vector_angle


def test_angle_vector_basic():
    alpha = 0
    beta = 0
    assert np.array_equal(angle_vector(alpha, beta), [0.0, 0.0, 1.0])


def test_angle_vector_complex():
    alpha = -30
    beta = 60
    # x is +0.25 because the pan angle goes clockwise,
    # therefore this negative one goes counterclockwise,
    # so towards the x-axis
    # This is the correct value, do not edit!!
    result = np.array([0.25, np.sqrt(3) / 2, np.sqrt(3) / 4])
    assert np.allclose(angle_vector(np.deg2rad(alpha), np.deg2rad(beta)), result)


def test_vector_angle_basic():
    assert vector_angle([0.0, 0.0, 1.0]) == (0, 0)


def test_vector_angle_complex_normalised():
    alpha = -30
    beta = 60
    (a, b) = vector_angle([0.25, np.sqrt(3)/2, np.sqrt(3)/4])
    assert pytest.approx(a) == np.deg2rad(alpha)
    assert pytest.approx(b) == np.deg2rad(beta)


def test_vector_angle_complex():
    """ not normalized, length of vector is 2 """
    alpha = -30
    beta = 60
    (a, b) = vector_angle([0.5, np.sqrt(3), np.sqrt(3)/2])
    assert pytest.approx(a) == np.deg2rad(alpha)
    assert pytest.approx(b) == np.deg2rad(beta)


def test_vector_angle_invalid():
    with pytest.raises(ValueError) as excinfo:
        vector_angle([0.0, 0.0, 0.0])
    assert "Vector not normalizable" == str(excinfo.value)


def test_vector_angle_invalid_type():
    with pytest.raises(TypeError) as excinfo:
        vector_angle([1, 2])
    assert "Vector must contain three floats" == str(excinfo.value)
