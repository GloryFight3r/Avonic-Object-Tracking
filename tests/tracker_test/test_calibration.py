import pytest
import numpy as np
import math

from avonic_speaker_tracker.calibration import Calibration

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
    assert cal.speaker_point == p

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
    assert cal.mic_to_cam == None
    assert cal.speaker_point == None
    assert cal.to_mic_direction == None
    assert cal.to_cam_direction == None

def test_is_calibrated():
    cal = Calibration()
    d = np.array([1, 1])
    p = (np.array([1, 1]), np.array([0, 0, 0]))

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
            (1, (np.array([0, 0]), np.array([0, -1, 0])), np.array([0, math.pi/4]), np.array([0, -1/2**0.5, -1/2**0.5]), np.array([0, -1, -1])),
            (1, (np.array([0, 0]), np.array([0, -1, 0])), np.array([math.pi/4, 0]), np.array([-1/2**0.5, -1/2**0.5, 0]), np.array([-1, 0, -1])),
            (2, (np.array([0, -math.pi/4]), np.array([0, -1, 0])), np.array([0, math.pi/4]), np.array([0, -1/2**0.5, -1/2**0.5]), np.array([0, -1, -1])),
            (4, (np.array([0, -0.245]), np.array([0, -4, 0])), np.array([0, 0.6435]), np.array([0, -3, -4]), np.array([0, -3, -4]))
    ]

@pytest.mark.parametrize("height, speaker, to_mic, to_cam, mic_to_cam", generate_calibration_setup())
def test_calculate_distance(height, speaker, to_mic, to_cam, mic_to_cam):
    cal = Calibration()
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
    cal.add_speaker_point((np.array([math.pi/2, 0]), np.array([0, -1, 0])))
    cal.add_direction_to_mic(np.array([math.pi/2, 0]))

    with pytest.raises(AssertionError):
        cal.calculate_distance()

def test_zero_height():
    cal = Calibration()
    cal.set_height(0)
    cal.add_speaker_point((np.array([0, -0.245]), np.array([0, -4, 0])))
    cal.add_direction_to_mic(np.array([0, 0.6435]))

    with pytest.raises(AssertionError):
        cal.calculate_distance()

    cal.add_speaker_point((np.array([0, -0.245]), np.array([1, 0, 0])))

    with pytest.raises(AssertionError):
        cal.calculate_distance()
