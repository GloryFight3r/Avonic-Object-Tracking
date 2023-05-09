import pytest

from microphone_api.microphone_adapter import Microphone

def test_set_height_adapter():
    mic = Microphone()
    assert mic.height == 0
    mic.set_height(10)
    assert mic.height == 10
