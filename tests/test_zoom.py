import pytest

from src.AvonicCameraApi.zoom import *

class CameraMock:
    """
    Mock camera class to artificially set the zoom value and keep track of amount of requests sent.
    """
    call_count = None
    zoom = None

    def __init__(self):
        self.call_count = 0
        self.zoom = 16384

    def send(self, header, command, data):
        if len(command) == 26:
            # to set the zoom of the camera
            hex_res = command[13] + command[16] + command[19] + command[22]
            print(hex_res.replace(" ", ""))
            self.zoom = int(hex_res, 16)

        self.call_count += 1
        message = "81 01 04 47 0p 0q 0r 0s FF"
        ret = insert_zoom_in_hex(message, self.zoom).replace(" ", "")[4:]
        return ret

def test_get_zoom():
    """
    Test to get the zoom from the Camera.
    """
    api = API(CameraMock())
    ret = api.get_zoom()
    assert ret == api.camera.zoom
    assert api.camera.call_count == 1

def test_direct_zoom():
    """
    Test to set the zoom of the camera.
    """
    api = API(CameraMock())

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
