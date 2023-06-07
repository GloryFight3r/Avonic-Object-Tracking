import pytest
from CameraMock import CameraMock
from avonic_camera_api.camera_control_api import CameraAPI, insert_zoom_in_hex
from avonic_camera_api.camera_adapter import ResponseCode


def test_get_zoom():
    """
    Test to get the zoom from the Camera.
    """
    api = CameraAPI(CameraMock())
    ret = api.get_zoom()
    assert ret == api.camera.zoom
    assert api.camera.call_count == 1

def test_direct_zoom():
    """
    Test to set the zoom of the camera.
    """
    api = CameraAPI(CameraMock())

    # Value of the zoom to set Camera to
    test_zoom = 100
    api.direct_zoom(test_zoom)
    assert api.camera.zoom == test_zoom
    assert api.camera.call_count == 1

def test_insert_zoom_in_hex():
    """
    Test to insert the zoom value into the hex message without throwing exceptions.
    """
    message = "81 01 04 47 0p 0q 0r 0s FF"
    zoom_values = [0, 100, 1000, 15000, 16384]
    results = [
                "81 01 04 47 00 00 00 00 FF",
                "81 01 04 47 00 00 06 04 FF",
                "81 01 04 47 00 03 0e 08 FF",
                "81 01 04 47 03 0a 09 08 FF",
                "81 01 04 47 04 00 00 00 FF"
              ]
    for test in zip(zoom_values, results):
        assert insert_zoom_in_hex(message, test[0]) == test[1]

def test_insert_zoom_out_of_range():
    """
    Test inserting zoom values that are out of range.
    """
    message = "81 01 04 47 0p 0q 0r 0s FF"
    with pytest.raises(AssertionError):
        insert_zoom_in_hex(message, 16385)

    with pytest.raises(AssertionError):
        insert_zoom_in_hex(message, -1)

def test_insert_zoom_wrong_size_hex():
    """
    Test with messages that are too long or too short.
    """
    short_message = "12 34 56 78 91 12"
    long_message = "12 34 56 78 91 12 34 56 78 91"
    with pytest.raises(AssertionError):
        insert_zoom_in_hex(short_message, 100)
    with pytest.raises(AssertionError):
        insert_zoom_in_hex(long_message, 100)


def test_timeout():
    api = CameraAPI(CameraMock(True))
    ret = api.get_zoom()
    assert ret == ResponseCode.TIMED_OUT
    assert api.camera.call_count == 0
