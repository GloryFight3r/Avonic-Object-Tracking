from microphone_api.stub_comms_microphone import *
import pytest

def test_azimuth():
    api = MicrophoneAPI()
    assert api.get_azimuth(46) == 46 

def test_azimuth_invalid():
    api = MicrophoneAPI()
    with pytest.raises(Exception):
        api.get_azimuth(56.7)

def test_elevation(): 
    api = MicrophoneAPI()
    assert api.get_elevation(90) == 90

def test_elevation_invalid():
    api = MicrophoneAPI()
    with pytest.raises(Exception):
        api.get_elevation(56.7)