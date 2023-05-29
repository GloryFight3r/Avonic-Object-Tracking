import numpy as np
from unittest import mock
from avonic_speaker_tracker.pointer import preset_pointer,continuous_pointer,point
from avonic_speaker_tracker.preset import PresetCollection


def test_preset_pointer_good_weather():
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True
    mic2_api = mock.Mock()
    mic2_api.get_direction.return_value = np.array([7, 8, 10])
    mic2_api.is_speaking.return_value = True
    col = PresetCollection()
    col.add_preset("preset", np.array([4, 7, 5000]), np.array([1, 2, 3]))
    col.add_preset("preset1", np.array([1, 5, 5000]), np.array([6, 8, 9]))
    dir1 = preset_pointer(mic_api,col)
    dir2 = preset_pointer(mic2_api,col)

    assert (dir1 == np.array([int(np.rad2deg(4)), int(np.rad2deg(7)), 5000])).all()
    assert (dir2 == np.array([int(np.rad2deg(1)), int(np.rad2deg(5)), 5000])).all()


def test_continuous_pointer():
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True

    mic2_api = mock.Mock()
    mic2_api.get_direction.return_value = np.array([5, 80, 10])
    mic2_api.is_speaking.return_value = True

    calibration = mock.Mock()
    calibration.to_mic_direction = np.array([0.0,-0.5,1.2])
    calibration.mic_height = 0.65

    dir1 = continuous_pointer(mic_api,calibration)
    dir2 = continuous_pointer(mic2_api,calibration)
    assert(dir1 == np.array([-8,3,0])).all()
    assert(dir2 == np.array([-1,6,0])).all()

def test_pointer():
    cam_api = mock.Mock()
    cam2_api = mock.Mock()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([7, 8, 9])
    mic_api.is_speaking.return_value = True
    col = PresetCollection()
    col.add_preset("preset2", np.array([5, 9, 5000]), np.array([7, 8, 10]))
    col.add_preset("preset3", np.array([1, 5, 5000]), np.array([6, 8, 9]))
    calibration = mock.Mock()
    calibration.to_mic_direction = np.array([0.0,-0.5,1.2])
    calibration.mic_height = 0.65

    dir1 = point(cam_api, mic_api, col, True, calibration)
    assert cam_api.move_absolute.call_count == 1
    assert cam_api.direct_zoom.call_count == 1
    dir2 = point(cam_api, mic_api, col, False, calibration)
    assert cam_api.move_absolute.call_count == 2
    assert cam_api.direct_zoom.call_count == 1

    dir3 = point(cam2_api, mic_api, col, False, calibration, np.array([-16,4,0]))
    assert cam2_api.move_absolute.call_count == 0
    assert cam2_api.direct_zoom.call_count == 0

    assert (dir1 == np.array([int(np.rad2deg(5)), int(np.rad2deg(9)), 5000])).all()
    assert (dir2 == np.array([-16,4,0])).all()
    assert (dir3 == np.array([-16,4,0])).all()
