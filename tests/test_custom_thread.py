from threading import Event
from unittest import mock
import numpy as np
from avonic_speaker_tracker.custom_thread import CustomThread


def test_constructor():
    e = Event()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([0, 0, 1])
    mic_api.is_speaking.return_value = True
    cam_api = mock.Mock()
    ct = CustomThread(e, '', cam_api, mic_api)
    assert ct.event == e
    assert ct.mic_api == mic_api
    assert ct.cam_api == cam_api
    assert ct.url == 'http://'
    assert ct.value is None


def test_setter():
    e = Event()
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([0, 0, 1])
    mic_api.is_speaking.return_value = True
    cam_api = mock.Mock()
    ct = CustomThread(e, '', mic_api, cam_api)
    assert ct.event == e
    assert ct.value is None
    ct.set_calibration(2)
    assert ct.value == 2
    ct.set_calibration((2, 1))
    assert ct.value == (2, 1)
