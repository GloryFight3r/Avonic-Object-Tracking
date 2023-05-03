from microphone_api.stub_comms_microphone import *
import pytest

def test_azimuth():
    assert get_azimuth(46) == 46 

def test_azimuth_invalid():
    with pytest.raises(Exception):
        get_azimuth(56.7)

def test_elevation(): 
    assert get_elevation(90) == 90

def test_elevation_invalid():
    with pytest.raises(Exception):
        get_elevation(56.7)