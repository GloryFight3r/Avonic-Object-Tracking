import pytest
import numpy as np
import math

from avonic_speaker_tracker.calibration import Calibration, angle_between_vectors

def test_set_height():
    cal = Calibration()
    # test the default height
    assert cal.mic_height == 1
    cal.set_height(2)
    assert cal.mic_height == 2

def test_add_speaker_point():
    cal = Calibration()
    p = (np.array([1, 1]), np.array([0, 0, 0]))
    cal.add_speaker_point(p)
    assert cal.speaker_points[0] == p

def test_add_direction_to_mic():
    cal = Calibration()
    d = np.array([1, 1])
    cal.add_direction_to_mic(d)
    assert (cal.to_mic_direction == d).all()

def test_reset_calibration():
    cal = Calibration()
    d = np.array([1, 1])
    p = (np.array([1, 1]), np.array([0, 0, 0]))

    cal.add_speaker_point(p)
    cal.add_direction_to_mic(d)

    cal.reset_calibration()
    assert cal.mic_to_cam is None
    assert not cal.speaker_points
    assert cal.to_mic_direction is None

def test_is_calibrated():
    cal = Calibration()
    d = np.array([1, 1, 1])
    p = (np.array([1, 1, 0]), np.array([0, 1.0, 0]))

    cal.add_speaker_point(p)
    assert not cal.is_calibrated()
    cal.add_direction_to_mic(d)
    assert cal.is_calibrated()

    cal.reset_calibration()
    cal.add_direction_to_mic(d)
    assert not cal.is_calibrated()
    cal.add_speaker_point((p))
    assert cal.is_calibrated()

    cal.reset_calibration()
    cal.add_direction_to_mic(d)
    assert not cal.is_calibrated()
    cal.add_speaker_point((p))
    assert cal.is_calibrated()


def generate_calibration_setup():
    return [
            (1,
                np.array([0.0, 2**0.5/2, 2**0.5/2]),
                (np.array([0., 0., 1.]), np.array([0, -1, 0])),
                np.array([0, -1, -1])
             ),
            (1,
                np.array([2**0.5/2, 0, 2**0.5/2]),
                (np.array([0., 0., 1.]), np.array([0, -1, 0])),
                np.array([-1, 0, -1])
             ),
            (2,
                np.array([0, 2**0.5/2, 2**0.5/2]),
                (np.array([0, -2**0.5/2, 2**0.5/2]), np.array([0, -1, 0])),
                np.array([0, -1, -1])
             ),
            (4,
                np.array([0.0, 0.6, 0.8]),
                (np.array([0, -0.24255632, 0.97013732]), np.array([0, -4, 0])),
                np.array([0, -3, -4])
             )
    ]

@pytest.mark.parametrize("height, to_mic, speaker, mic_to_cam", generate_calibration_setup())
def test_calculate_distance(height, to_mic, speaker, mic_to_cam):
    cal = Calibration()
    cal.reset_calibration()
    cal.set_height(height)
    cal.add_speaker_point(speaker)
    cal.add_direction_to_mic(to_mic)
    cal.calculate_distance()
    e = 1E-4
    assert abs(cal.mic_to_cam[0] - mic_to_cam[0]) <= e
    assert abs(cal.mic_to_cam[1] - mic_to_cam[1]) <= e
    assert abs(cal.mic_to_cam[2] - mic_to_cam[2]) <= e

def test_calculate_distance_one_line():
    cal = Calibration()
    cal.set_height(1)
    cal.add_speaker_point((np.array([1, 1, 0]), np.array([0, -1, 0])))
    cal.add_direction_to_mic(np.array([1, 1, 0]))

    with pytest.raises(AssertionError):
        cal.calculate_distance()

def test_zero_height():
    cal = Calibration()
    cal.set_height(0)
    cal.add_speaker_point((np.array([0, -0.24255632, 0.97013732]), np.array([0, -4, 0])))
    cal.add_direction_to_mic(np.array([0, 0.6, 0.8]))

    with pytest.raises(AssertionError):
        cal.calculate_distance()

    cal.add_speaker_point((np.array([0, -0.24255632, 0.97013732]), np.array([1, 0, 0])))

    with pytest.raises(AssertionError):
        cal.calculate_distance()


def generate_vectors_angles():
    return [
        ([1, 1, 1], [2, 2, 2], 1),
        ([1, 0, 0], [0, 1, 1], np.cos(math.pi/2)),
        ([1, 0, 0], [1, 1, 0], np.cos(math.pi/4)),
    ]

@pytest.mark.parametrize("v1, v2, exp_angle", generate_vectors_angles())
def test_angle_between_vectors(v1, v2, exp_angle):
    angle = angle_between_vectors(np.array(v1), np.array(v2))
    # floats are not exactly the same in this case
    assert abs(angle - exp_angle) <= 1E-4
