import pytest

from microphone_api.microphone_adapter import Microphone
from microphone_api.microphone_control_api import MicrophoneAPI

def test_set_height_api():
    mic = Microphone()
    api = MicrophoneAPI(mic)
    assert api.microphone.height == 0
    api.set_height(10)
    assert api.microphone.height == 10

def test_set_height_negative():
    mic = Microphone()
    api = MicrophoneAPI(mic)
    with pytest.raises(AssertionError):
        api.set_height(-1)

def test_set_height_float():
    mic = Microphone()
    api = MicrophoneAPI(mic)
    api.set_height(2.5)
    assert api.microphone.height == 2.5

def test_azimuth():
    mic = Microphone()
    api = MicrophoneAPI(mic)
    assert api.get_azimuth(46) == 46

def test_azimuth_invalid():
    mic = Microphone()
    api = MicrophoneAPI(mic)
    with pytest.raises(Exception):
        api.get_azimuth(56.7)

def test_elevation():
    mic = Microphone()
    api = MicrophoneAPI(mic)
    assert api.get_elevation(90) == 90

def test_elevation_invalid():
    mic = Microphone()
    api = MicrophoneAPI(mic)
    with pytest.raises(Exception):
        api.get_elevation(56.7)
