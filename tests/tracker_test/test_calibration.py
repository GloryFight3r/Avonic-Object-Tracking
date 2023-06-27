import math
import os
from unittest import mock
import json
import pytest
import numpy as np

from maat_tracking.audio_model.calibration import Calibration, angle_between_vectors

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
    assert cal.mic_to_cam[0] == 0.0
    assert cal.mic_to_cam[1] == 0.0
    assert cal.mic_to_cam[2] == 0.0
    assert not cal.speaker_points
    assert np.allclose(cal.to_mic_direction, np.array([0, 0, 0]))

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

def test_with_file():
    try:
        cal = Calibration("TEST_WITH_FILE_CALIBRATION.json")
        d = np.array([1, 1, 1])
        p = (np.array([1, 0.2, 0]), np.array([0, 0.2, 1]))

        cal.add_speaker_point(p)
        cal.add_direction_to_mic(d)
        second_cal = Calibration("TEST_WITH_FILE_CALIBRATION.json")
        print(cal.to_mic_direction, second_cal.to_mic_direction)
        print(cal.speaker_points[0], second_cal.speaker_points[0])
        assert np.allclose(cal.to_mic_direction, second_cal.to_mic_direction)
        assert len(cal.speaker_points) == len(second_cal.speaker_points) == 1
        assert np.allclose(cal.speaker_points[0], second_cal.speaker_points[0])
    finally:
        os.remove("TEST_WITH_FILE_CALIBRATION.json")

def test_with_file_corrupted_to_mic():
    try:
        data = {
            "speaker_points": [
                [
                    [
                        -0.1566478190028709,
                        0.058144828910475836,
                        0.9859414991127086
                    ],
                    [
                        -0.5147397816609846,
                        -0.39073112848927377,
                        -0.7631331092313455
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        -0.5607285742301801,
                        -0.45399049973954675,
                        0.6924421219048029
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        0.8243025903159147,
                        -0.4694715627858908,
                        0.31642011840881235
                    ]
                ]
            ],
            "to_mic_direction": [
                0.21048846637682528,
                0.1497270856790396
            ],
            "mic_height": 1.0
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_to_mic.json", 'w') as outfile:
            outfile.write(json_string)

        cal = Calibration("test_with_file_corrupted_to_mic.json")
        assert np.allclose(cal.to_mic_direction, Calibration.default_to_mic)
    finally:
        os.remove("test_with_file_corrupted_to_mic.json")

def test_with_file_corrupted_one_mic():
    try:
        data = {
            "speaker_points": [
                [
                    [
                        -0.1566478190028709,
                        0.058144828910475836,
                        0.9859414991127086
                    ],
                    [
                        -0.5147397816609846,
                        -0.39073112848927377
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        -0.5607285742301801,
                        -0.45399049973954675,
                        0.6924421219048029
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        0.8243025903159147,
                        -0.4694715627858908,
                        0.31642011840881235
                    ]
                ]
            ],
            "to_mic_direction": [
                0.21048846637682528,
                0.1497270856790396,
                0
            ],
            "mic_height": 1.0
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_one_mic.json", 'w') as outfile:
            outfile.write(json_string)

        cal = Calibration("test_with_file_corrupted_one_mic.json")
        assert np.allclose(cal.speaker_points[0][1], Calibration.default_mic_vec)
    finally:
        os.remove("test_with_file_corrupted_one_mic.json")

def test_with_file_corrupted_one_cam():
    try:
        data = {
            "speaker_points": [
                [
                    [
                        -0.1566478190028709,
                        0.058144828910475836
                    ],
                    [
                        -0.5147397816609846,
                        -0.39073112848927377,
                        -0.7631331092313455
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        -0.5607285742301801,
                        -0.45399049973954675,
                        0.6924421219048029
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        0.8243025903159147,
                        -0.4694715627858908,
                        0.31642011840881235
                    ]
                ]
            ],
            "to_mic_direction": [
                0.21048846637682528,
                0.1497270856790396,
                0
            ],
            "mic_height": 1.0
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_one_cam.json", 'w') as outfile:
            outfile.write(json_string)

        cal = Calibration("test_with_file_corrupted_one_cam.json")
        assert np.allclose(cal.speaker_points[0][0], Calibration.default_camera_vec)
    finally:
        os.remove("test_with_file_corrupted_one_cam.json")

def test_with_file_corrupted_missed_one_cam():
    try:
        data = {
            "speaker_points": [
                [
                    [
                        -0.1566478190028709,
                        0.058144828910475836,
                        0.9859414991127086
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        -0.5607285742301801,
                        -0.45399049973954675,
                        0.6924421219048029
                    ]
                ],
                [
                    [
                        0.023023299547353826,
                        0.016967664563590747,
                        0.9995909293492065
                    ],
                    [
                        0.8243025903159147,
                        -0.4694715627858908,
                        0.31642011840881235
                    ]
                ]
            ],
            "to_mic_direction": [
                0.21048846637682528,
                0.1497270856790396,
                0
            ],
            "mic_height": 1.0
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_missed_one_cam.json", 'w') as outfile:
            outfile.write(json_string)

        cal = Calibration("test_with_file_corrupted_missed_one_cam.json")
        assert np.allclose(cal.speaker_points[0][0], Calibration.default_camera_vec)
    finally:
        os.remove("test_with_file_corrupted_missed_one_cam.json")

def test_with_file_corrupted_speaker_points_missing():
    try:
        data = {
            "to_mic_direction": [
                0.21048846637682528,
                0.1497270856790396,
                0
            ],
            "mic_height": 1.7
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_speaker_points_missing.json", 'w') as outfile:
            outfile.write(json_string)

        cal = Calibration("test_with_file_corrupted_speaker_points_missing.json")
        assert len(cal.speaker_points) == 0
        assert np.allclose(cal.to_mic_direction,
            np.array([0.21048846637682528, 0.1497270856790396, 0]))
        assert cal.mic_height == 1.7
    finally:
        os.remove("test_with_file_corrupted_speaker_points_missing.json")

def test_with_file_corrupted_height_missing():
    try:
        data = {
            "to_mic_direction": [
                0.21048846637682528,
                0.1497270856790396,
                0
            ]
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_height_missing.json", 'w') as outfile:
            outfile.write(json_string)

        cal = Calibration("test_with_file_corrupted_height_missing.json")
        assert len(cal.speaker_points) == 0
        assert np.allclose(cal.to_mic_direction,
            np.array([0.21048846637682528, 0.1497270856790396, 0]))
        assert cal.mic_height == Calibration.default_height
    finally:
        os.remove("test_with_file_corrupted_height_missing.json")

def test_with_file_corrupted_to_mic_missing():
    try:
        data = {
            "mic_height": 1.7
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_to_mic_missing.json", 'w') as outfile:
            outfile.write(json_string)

        cal = Calibration("test_with_file_corrupted_to_mic_missing.json")
        assert len(cal.speaker_points) == 0
        assert np.allclose(cal.to_mic_direction, Calibration.default_to_mic)
        assert cal.mic_height == 1.7
    finally:
        os.remove("test_with_file_corrupted_to_mic_missing.json")

def test_set_filename():
    def mock_load(self):
        pass

    with mock.patch("maat_tracking.audio_model.calibration.Calibration.load", mock_load):
        cal = Calibration()
        assert cal.filename == ""
        cal.set_filename("asdf")
        assert cal.filename == "asdf"
