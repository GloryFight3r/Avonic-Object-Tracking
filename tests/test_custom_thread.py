from threading import Event

from avonic_speaker_tracker.custom_thread import CustomThread

def test_constructor():
    e = Event()
    ct = CustomThread(e)
    assert ct.event == e
    assert ct.value is None

def test_setter():
    e = Event()
    ct = CustomThread(e)
    assert ct.event == e
    assert ct.value is None
    ct.set_calibration(2)
    assert ct.value == 2
    ct.set_calibration((2, 1))
    assert ct.value == (2, 1)
