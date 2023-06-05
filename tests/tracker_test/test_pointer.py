import numpy as np
from unittest import mock
from avonic_speaker_tracker.preset_model.preset import PresetCollection
from avonic_speaker_tracker.preset_model.PresetModel import PresetModel
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel


def test_preset_pointer_good_weather():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.latest_direction = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True
    mic2_api = mock.Mock()
    mic2_api.latest_direction = np.array([7, 8, 10])
    mic2_api.get_direction.return_value = np.array([7, 8, 10])
    mic2_api.is_speaking.return_value = True
    pm = PresetModel()
    mic_api.get_direction.return_value = "some error"
    dir0 = pm.point(cam_api, mic_api)
    assert (dir0 == pm.prev_dir).all()
    assert (dir0 == np.array([0, 0, 1])).all()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    dir0 = pm.point(cam_api, mic_api)
    assert (dir0 == pm.prev_dir).all()
    pm.preset_locations.add_preset("preset", np.array([4, 7, 5000]), np.array([1, 2, 3]))
    pm.preset_locations.add_preset("preset1", np.array([1, 5, 5000]), np.array([6, 8, 9]))

    dir1 = pm.point(cam_api, mic_api)
    dir2 = pm.point(cam_api, mic2_api)

    assert (dir1 == np.array([int(np.rad2deg(4)), int(np.rad2deg(7)), 5000])).all()
    assert (dir2 == np.array([int(np.rad2deg(1)), int(np.rad2deg(5)), 5000])).all()


def test_continuous_pointer():
    cam_api = mock.Mock()
    mic_api = mock.Mock()

    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.latest_direction = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True

    mic2_api = mock.Mock()
    mic2_api.get_direction.return_value = np.array([5, 80, 10])
    mic2_api.latest_direction = np.array([5, 80, 10])
    mic2_api.is_speaking.return_value = True

    am = AudioModel()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am.calibration = calibration

    mic_api.get_direction.return_value = "some error"
    dir0 = am.point(cam_api, mic_api)
    assert (dir0 == am.prev_dir).all()
    assert (dir0 == np.array([0, 0, 1])).all()
    mic_api.get_direction.return_value = np.array([1, 2, 3])

    dir1 = am.point(cam_api, mic_api)
    dir2 = am.point(cam_api, mic2_api)
    assert(dir1 == np.array([-8,3,0])).all()
    assert(dir2 == np.array([-1,6,0])).all()
