from threading import Event

from avonic_speaker_tracker.custom_thread import CustomThread

def test_constructor():
    e = Event()
    ct = CustomThread(e)
    assert ct.event == e
    assert ct.calibration is None

def test_setter():
    e = Event()
    ct = CustomThread(e)
    assert ct.event == e
    assert ct.calibration is None
    ct.set_calibration(2)
    assert ct.calibration == 2
    ct.set_calibration((2, 1))
    assert ct.calibration == (2, 1)
