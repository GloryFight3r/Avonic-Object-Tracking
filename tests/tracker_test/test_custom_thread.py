from unittest import mock
from multiprocessing import Value
import numpy as np
from maat_tracking.updater import UpdateThread


def test_constructor():
    e = Value("i", 0, lock=False)
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([0, 0, 1])
    mic_api.is_speaking.return_value = True
    cam_api = mock.Mock()
    model = mock.Mock()
    ct = UpdateThread(e, cam_api, mic_api, model, "")
    assert ct.event == e
    assert ct.mic_api == mic_api
    assert ct.cam_api == cam_api
    assert ct.value == 0


def test_setter():
    e = Value("i", 0, lock=False)
    mic_api = mock.Mock()
    mic_api.get_direction.return_value = np.array([0, 0, 1])
    mic_api.is_speaking.return_value = True
    cam_api = mock.Mock()
    model = mock.Mock()
    ct = UpdateThread(e, cam_api, mic_api, model)
    assert ct.event == e
    assert ct.value == 0
    e.value = 1
    ct.start()
    e.value = 0
    ct.join()
