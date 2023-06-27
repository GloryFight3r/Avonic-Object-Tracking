from unittest import mock
import numpy as np
from maat_tracking.preset_model.PresetModel import PresetModel
from maat_tracking.audio_model.AudioModel import AudioModel
from maat_tracking.audio_model.AudioModelNoAdaptiveZoom import AudioModelNoAdaptiveZoom


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
    pm = PresetModel(cam_api, mic_api)
    pm2 = PresetModel(cam_api, mic2_api)
    pm.sleep()
    mic_api.get_direction.return_value = "some error"
    dir0 = pm.point()
    assert (dir0 == pm.prev_dir).all()
    assert (dir0 == np.array([0, 0, 1])).all()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    dir0 = pm.point()
    assert (dir0 == pm.prev_dir).all()
    pm.preset_locations.add_preset("preset", np.array([4, 7, 5000]), np.array([1, 2, 3]))
    pm.preset_locations.add_preset("preset1", np.array([1, 5, 4000]), np.array([6, 8, 9]))
    pm2.preset_locations.add_preset("preset", np.array([4, 7, 5000]), np.array([1, 2, 3]))
    pm2.preset_locations.add_preset("preset1", np.array([1, 5, 4000]), np.array([6, 8, 9]))

    dir1 = pm.point()
    dir2 = pm2.point()

    assert np.allclose(dir1, np.array([-131, 41, 5000]))
    assert np.allclose(dir2, np.array([57, -74, 4000]))

def test_preset_prev_dir():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.latest_direction = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True
    pm = PresetModel(cam_api, mic_api)
    pm.preset_locations.add_preset("preset", np.array([4, 7, 5000]), np.array([1, 2, 3]))
    pm.preset_locations.add_preset("preset1", np.array([1, 5, 4000]), np.array([6, 8, 9]))
    pm.point()
    cam_api.move_absolute.assert_called_with(24, 20, -131, 41)
    cam_api.direct_zoom.assert_called_with(5000)
    pm.point()
    cam_api.direct_zoom.assert_called_with(5000)
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

    am = AudioModel(cam_api, mic_api)
    am.sleep()
    am2 = AudioModel(cam_api, mic2_api)
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am.calibration = calibration
    am2.calibration = calibration

    mic_api.get_direction.return_value = "some error"
    dir0 = am.point()
    assert (dir0 == am.prev_dir).all()
    assert (dir0 == [0, 0, 1]).all()
    mic_api.get_direction.return_value = np.array([1, 2, 3])

    dir1 = am.point()
    am.point()
    assert cam_api.move_absolute.call_count == 1
    cam_api.direct_zoom.assert_called_with(3526)
    dir2 = am2.point()
    cam_api.direct_zoom.assert_called_with(2065)
    assert (dir1 == np.array([-8,3,3526])).all()
    assert (dir2 == np.array([-1,6,2065])).all()

def test_continuous_pointer_without_adaptive_zooming():
    cam_api = mock.Mock()
    mic_api = mock.Mock()

    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.latest_direction = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True

    mic2_api = mock.Mock()
    mic2_api.get_direction.return_value = np.array([7, 80, 12])
    mic2_api.latest_direction = np.array([7, 80, 12])
    mic2_api.is_speaking.return_value = True

    am = AudioModelNoAdaptiveZoom(cam_api, mic_api)
    am2 = AudioModelNoAdaptiveZoom(cam_api, mic2_api)
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am.calibration = calibration
    am2.calibration = calibration

    mic_api.get_direction.return_value = "some error"
    dir0 = am.point()
    assert (dir0 == am.prev_dir).all()
    assert (dir0 == np.array([0, 0, 1])).all()
    mic_api.get_direction.return_value = np.array([3, 4, 5])

    dir1 = am.point()
    am.point()
    assert cam_api.move_absolute.call_count == 1
    assert cam_api.direct_zoom.call_count == 0
    dir2 = am2.point()
    assert cam_api.direct_zoom.call_count == 0
    assert(dir1 == np.array([-13,4,1])).all()
    assert(dir2 == np.array([-2,6,1])).all()

def test_cont_tracker_no_zoom():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1.0,54.0,5.0])
    mic_api.latest_direction = np.array([1.0,54.0,5.0])
    mic_api.is_speaking.return_value = True
    am = AudioModelNoAdaptiveZoom(cam_api, mic_api)
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,0.0,1.0])
    calibration.mic_height = -0.65
    am.calibration = calibration
    am.point()
    cam_api.move_absolute.assert_called_with(13,15,0,31)

def test_zoom():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic2_api = mock.Mock()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel(cam_api, mic_api)
    am2 = AudioModel(cam_api, mic2_api)
    am.calibration = calibration
    am2.calibration = calibration
    mic_api.latest_direction = np.array([0.0,1.0,14.0])
    mic_api.get_direction.return_value = np.array([0.0,1.0,14.0])
    mic2_api.latest_direction = np.array([1.0,0.7,-2.0])
    mic2_api.get_direction.return_value = np.array([1.0,0.7,-2.0])

    dir1 = am.point()
    assert (dir1 == np.array([0,0,16000])).all()
    cam_api.direct_zoom.assert_called_with(16000)

    dir2 = am2.point()
    assert (dir2 == np.array([-125,7,1835])).all()
    cam_api.direct_zoom.assert_called_with(1835)



def test_preset_more():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.latest_direction = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True
    mic_api_pre = mock.Mock()
    mic_api_pre.get_direction.return_value = np.array([7, 7, 7])
    mic_api_pre.latest_direction = np.array([7, 7, 7])
    mic_api_pre.is_speaking.return_value = True
    mic2_api = mock.Mock()
    mic2_api.latest_direction = np.array([6, 8, 9])
    mic2_api.get_direction.return_value = np.array([6, 8, 9])
    mic2_api.is_speaking.return_value = True
    mic3_api = mock.Mock()
    mic3_api.get_direction.return_value = np.array([11, 12, 13])
    mic3_api.is_speaking.return_value = True
    mic4_api = mock.Mock()
    mic4_api.latest_direction = np.array([14, 15, 16])
    mic4_api.get_direction.return_value = np.array([14, 15, 16])
    mic4_api.is_speaking.return_value = True

    pm = PresetModel(cam_api, mic_api)
    #pm.prev_dir = np.array([22,-29,5000])
    pm.preset_locations.add_preset("pre", np.array([np.deg2rad(-160),
        np.deg2rad(-29), 5000]), np.array([7, 7, 7]))
    pm.preset_locations.add_preset("preset", np.array([np.deg2rad(-160),
        np.deg2rad(88), 5000]), np.array([1, 2, 3]))
    pm.preset_locations.add_preset("preset1", np.array([np.deg2rad(170),
        np.deg2rad(88), 5000]), np.array([6, 8, 9]))
    pm.preset_locations.add_preset("preset2", np.array([np.deg2rad(100),
        np.deg2rad(88), 5000]), np.array([11, 12, 13]))
    pm.preset_locations.add_preset("preset3", np.array([np.deg2rad(100),
        np.deg2rad(40), 5000]), np.array([14, 15, 16]))

    pm2 = PresetModel(cam_api, mic2_api)
    pm2.preset_locations = pm.preset_locations
    pm3 = PresetModel(cam_api, mic3_api)
    pm3.preset_locations = pm.preset_locations
    pm4 = PresetModel(cam_api, mic4_api)
    pm4.preset_locations = pm.preset_locations

    #pm.point(cam_api,mic_api_pre)
    pm.point()
    cam_api.move_absolute.assert_called_with(24,20,-160,88)

    pm2.point()
    cam_api.move_absolute.assert_called_with(24,20,170,88)

    pm3.point()
    cam_api.move_absolute.assert_called_with(24,20,100,88)

    pm4.point()
    cam_api.move_absolute.assert_called_with(24,20,100,40)


def test_various_speed_X_axis_audio():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel(cam_api, mic_api)
    am1 = AudioModelNoAdaptiveZoom(cam_api, mic_api)
    am.prev_dir = np.array([-80,0,0])
    am1.prev_dir = np.array([-80,0,0])
    am.calibration = calibration
    am1.calibration = calibration
    mic_api.latest_direction = np.array([0.0,0.7,-10.0])
    mic_api.get_direction.return_value = np.array([0.0,0.7,-10.0])
    am.point()
    cam_api.move_absolute.assert_called_with(24, 11, 180, 1)
    cam_api.direct_zoom.assert_called_with(12939)
    am.prev_dir = np.array([60,0,0])
    am.point()
    cam_api.move_absolute.assert_called_with(20, 11, 180, 1)

    am1.prev_dir = np.array([60,0,0])
    am.point()
    cam_api.move_absolute.assert_called_with(20, 11, 180, 1)
    mic_api.latest_direction = np.array([0.0,1.8,-10.0])
    mic_api.get_direction.return_value = np.array([0.0,1.8,-10.0])
    am1.point()
    cam_api.move_absolute.assert_called_with(20, 11, 180, 3)

def test_various_speed_Y_axis_audio():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel(cam_api, mic_api)
    am1 = AudioModelNoAdaptiveZoom(cam_api, mic_api)
    am.prev_dir = np.array([0,88,0])
    am1.prev_dir = np.array([0,88,0])
    am.calibration = calibration
    am1.calibration = calibration
    mic_api.latest_direction = np.array([1.0,-3.7,-0.3])
    mic_api.get_direction.return_value = np.array([1.0,-3.7,-0.3])
    am.point()
    cam_api.move_absolute.assert_called_with(13, 20, 7, 6)

    am.prev_dir = np.array([0,40,0])
    am.point()
    cam_api.move_absolute.assert_called_with(13, 16, 7, 6)

    mic_api.latest_direction = np.array([1.0,-4.7,-0.3])
    mic_api.get_direction.return_value = np.array([1.0,-4.7,-0.3])
    am1.point()
    cam_api.move_absolute.assert_called_with(13, 20, 6, 6)

    am1.prev_dir = np.array([0,40,0])
    am1.point()
    cam_api.move_absolute.assert_called_with(13, 16, 6, 6)


def test_zoom_out():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    mic_api.is_speaking.return_value = False
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel(cam_api, mic_api)
    am.prev_dir = np.array([0,0,16000])
    am.set_speak_delay(100)
    am.calibration = calibration
    mic_api.get_direction.return_value = np.array([0.0,1.0,14.0])
    am.point()
    assert cam_api.direct_zoom.call_count == 1
    cam_api.direct_zoom.assert_called_with(0)
    assert cam_api.move_absolute.call_count == 0

def test_speak_delay():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    mic_api.is_speaking.return_value = True
    calibration.mic_to_cam = -np.array([0.4,-1.5,3.7])
    calibration.mic_height = -0.65
    am = AudioModel(cam_api, mic_api)
    am.calibration = calibration
    mic_api.get_direction.return_value = np.array([1.2,0.7,-1.4])
    am.point()
    assert (am.prev_dir==np.array([-32,-16,4739])).all()
    cam_api.direct_zoom.assert_called_with(4739)

    mic_api.is_speaking.return_value = False
    am.set_speak_delay(100)

    am.point()
    assert (am.prev_dir==np.array([-32,-16,0])).all()
    cam_api.direct_zoom.assert_called_with(0)
