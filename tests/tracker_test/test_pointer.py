from unittest import mock
import numpy as np
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

    assert np.allclose(dir1, np.array([np.rad2deg(4), np.rad2deg(7), 5000]))
    assert np.allclose(dir2, np.array([np.rad2deg(1), np.rad2deg(5), 5000]))

def test_preset_prev_dir():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.latest_direction = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True
    pm = PresetModel()
    pm.preset_locations.add_preset("preset", np.array([4, 7, 5000]), np.array([1, 2, 3]))
    pm.preset_locations.add_preset("preset1", np.array([1, 5, 5000]), np.array([6, 8, 9]))
    dir0 = pm.point(cam_api,mic_api)
    cam_api.move_absolute.assert_called_with(24, 20, 229.1831180523293, 401.07045659157626)
    dir1 = pm.point(cam_api,mic_api)

    assert cam_api.move_absolute.call_count == 1


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
    assert(dir1 == np.array([-8,3,3526])).all()
    assert(dir2 == np.array([-1,6,2065])).all()

def test_zoom():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic2_api = mock.Mock()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel()
    am.calibration = calibration
    mic_api.latest_direction = np.array([0.0,1.0,14.0])
    mic_api.get_direction.return_value = np.array([0.0,1.0,14.0])
    mic2_api.latest_direction = np.array([1.0,0.7,-2.0])
    mic2_api.get_direction.return_value = np.array([1.0,0.7,-2.0])

    dir1 = am.point(cam_api,mic_api)
    assert(dir1 == np.array([0,0,16000])).all()

    dir2 = am.point(cam_api,mic2_api)
    assert(dir2 == np.array([-125,7,1835])).all()

def test_various_speed():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel()
    am.calibration = calibration
    mic_api.latest_direction = np.array([1.0,0.7,-2.0])
    mic_api.get_direction.return_value = np.array([5.0,3.7,-2.0])
    dir1 = am.point(cam_api,mic_api)
    cam_api.move_absolute.assert_called_with(15, 12, -45, 7)

def test_zoom_out():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    mic_api.is_speaking = False
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel()
    am.prev_dir = np.array([0,0,16000])
    am.set_speak_delay(100)
    am.calibration = calibration
    mic_api.get_direction.return_value = np.array([0.0,1.0,14.0])
    am.point(cam_api,mic_api)
    assert cam_api.direct_zoom.call_count == 1
    assert cam_api.move_absolute.call_count == 0
