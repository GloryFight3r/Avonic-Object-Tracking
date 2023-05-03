import pytest

from src.AvonicCameraApi.zoom import *

class CameraMock:
    call_count = None
    zoom = None

    def __init__(self):
        self.call_count = 0

    def send(self, header, command, data):
        self.call_count += 1
        return "905004000000FF" # max zoom

def test_get_zoom():
    api = API(CameraMock())
    ret = api.get_zoom()
    assert ret == 16384
    assert api.call_count == 1

#def test_direct_zoom():
#    api = API(CameraMock())
#
#    # Value of the zoom to set Camera to
#    test_zoom = 100
#    api.direct_zoom()
#    assert api.get_zoom() == test_zoom


def test_insert_zoom_in_hex():
    messages = "81 01 04 47 0p 0q 0r 0s FF"
    zoom_values = [0, 100, 1000, 15000, 16384]
    results = [
                "81 01 04 47 00 00 00 00 FF",
                "81 01 04 47 00 00 06 04 FF",
                "81 01 04 47 00 03 0E 08 FF",
                "81 01 04 47 03 0A 09 08 FF",
                "81 01 04 47 0F 0F 0F 0F FF"
              ]
    for test in zoom_values.zip(results):
        assert insert_zoom_in_hex(message, test[0]) == test[1]

    with pytest.raises(Exception):
        insert_zoom_in_hex(message, 16385)

    with pytest.raises(Exception):
        insert_zoom_in_hex(message, -1)
