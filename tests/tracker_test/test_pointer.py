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
    pm.preset_locations.add_preset("preset1", np.array([1, 5, 4000]), np.array([6, 8, 9]))

    dir1 = pm.point(cam_api, mic_api)
    cam_api.direct_zoom.assert_called_with(5000)    
    dir2 = pm.point(cam_api, mic2_api)
    cam_api.direct_zoom.assert_called_with(4000)    

    assert np.allclose(dir1, np.array([-131, 41, 5000]))
    assert np.allclose(dir2, np.array([57, -74, 4000]))

def test_preset_prev_dir():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    mic_api.latest_direction = np.array([1, 2, 3])
    mic_api.is_speaking.return_value = True
    pm = PresetModel()
    pm.preset_locations.add_preset("preset", np.array([4, 7, 5000]), np.array([1, 2, 3]))
    pm.preset_locations.add_preset("preset1", np.array([1, 5, 4000]), np.array([6, 8, 9]))
    dir0 = pm.point(cam_api,mic_api)
    cam_api.move_absolute.assert_called_with(21, 17, -131, 41)
    cam_api.direct_zoom.assert_called_with(5000)    
    dir1 = pm.point(cam_api,mic_api)
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
    am.point(cam_api, mic_api)
    assert cam_api.move_absolute.call_count == 1
    cam_api.direct_zoom.assert_called_with(3526)    
    dir2 = am.point(cam_api, mic2_api)
    cam_api.direct_zoom.assert_called_with(2065)    
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
    cam_api.direct_zoom.assert_called_with(16000)    

    dir2 = am.point(cam_api,mic2_api)
    assert(dir2 == np.array([-125,7,1835])).all()
    cam_api.direct_zoom.assert_called_with(1835)    



def test_various_speed_preset():
    cam_api = mock.Mock()
    cam3_api = mock.Mock()
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
    mic3_api.latest_direction = np.array([11, 12, 13])
    mic3_api.get_direction.return_value = np.array([11, 12, 13])
    mic3_api.is_speaking.return_value = True
    mic4_api = mock.Mock()
    mic4_api.latest_direction = np.array([14, 15, 16])
    mic4_api.get_direction.return_value = np.array([14, 15, 16])
    mic4_api.is_speaking.return_value = True

    pm = PresetModel()
    #pm.prev_dir = np.array([22,-29,5000])
    pm.preset_locations.add_preset("pre", np.array([np.deg2rad(-160), np.deg2rad(-29), 5000]), np.array([7, 7, 7]))
    pm.preset_locations.add_preset("preset", np.array([np.deg2rad(-160), np.deg2rad(88), 5000]), np.array([1, 2, 3]))
    pm.preset_locations.add_preset("preset1", np.array([np.deg2rad(170), np.deg2rad(88), 5000]), np.array([6, 8, 9]))
    pm.preset_locations.add_preset("preset2", np.array([np.deg2rad(100), np.deg2rad(88), 5000]), np.array([11, 12, 13]))
    pm.preset_locations.add_preset("preset3", np.array([np.deg2rad(100), np.deg2rad(40), 5000]), np.array([14, 15, 16]))

    pm.point(cam_api,mic_api_pre)
    print(pm.prev_dir)
    dir1 = pm.point(cam_api, mic_api)
    cam_api.move_absolute.assert_called_with(13,20,-160,88)
    dir2 = pm.point(cam_api, mic2_api)
    cam_api.move_absolute.assert_called_with(24,11,170,88)
    pm.point(cam_api,mic3_api)
    cam_api.move_absolute.assert_called_with(17,11,100,88)
    pm.point(cam_api,mic4_api)
    cam_api.move_absolute.assert_called_with(13,18,100,40)


def test_various_speed_X_axis_audio():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel()
    am.prev_dir = np.array([-80,0,0])
    am.calibration = calibration
    mic_api.latest_direction = np.array([0.0,0.7,-10.0])
    mic_api.get_direction.return_value = np.array([0.0,0.7,-10.0])
    dir1 = am.point(cam_api,mic_api)
    cam_api.move_absolute.assert_called_with(24, 11, 180, 1)  
    cam_api.direct_zoom.assert_called_with(12939)
    am.prev_dir = np.array([60,0,0])
    am.point(cam_api,mic_api)
    cam_api.move_absolute.assert_called_with(20, 11, 180, 1)  

def test_various_speed_Y_axis_audio():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    calibration.mic_to_cam = -np.array([0.0,-0.5,1.2])
    calibration.mic_height = -0.65
    am = AudioModel()
    am.prev_dir = np.array([0,88,0])
    am.calibration = calibration
    mic_api.latest_direction = np.array([1.0,-3.7,-0.3])
    mic_api.get_direction.return_value = np.array([1.0,-3.7,-0.3])
    dir1 = am.point(cam_api,mic_api)
    cam_api.move_absolute.assert_called_with(13, 20, 7, 6)

    am.prev_dir = np.array([0,40,0])
    am.point(cam_api,mic_api)
    cam_api.move_absolute.assert_called_with(13, 16, 7, 6)

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
    cam_api.direct_zoom.assert_called_with(0)
    assert cam_api.move_absolute.call_count == 0

def test_speak_delay():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    calibration = mock.Mock()
    mic_api.is_speaking = True
    calibration.mic_to_cam = -np.array([0.4,-1.5,3.7])
    calibration.mic_height = -0.65
    am = AudioModel() 
    am.calibration = calibration
    mic_api.get_direction.return_value = np.array([1.2,0.7,-1.4])
    am.point(cam_api,mic_api)
    assert (am.prev_dir==np.array([-32,-16,4739])).all()
    cam_api.direct_zoom.assert_called_with(4739)    

    mic_api.is_speaking = False
    am.set_speak_delay(100)

    am.point(cam_api,mic_api)
    assert (am.prev_dir==np.array([-32,-16,0])).all()
    cam_api.direct_zoom.assert_called_with(0)    
