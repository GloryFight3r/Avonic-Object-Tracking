from unittest import mock
import pytest

from maat_camera_api.camera_http_request import ResponseCodeHTTP
from maat_camera_api.camera_http_request import CameraHTTP

class MockResponse:
    def __init__(self, status_code, content):
        self.status_code = status_code
        self.content = content

    def json(self):
        return self.content

@pytest.fixture()
def http_camera():
    cam = CameraHTTP(("0.0.0.0", 80))

    return cam


def test_normal_command(http_camera, monkeypatch):
    http_camera.address = ("0.0.12.13", 80)
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = MockResponse(200, "mocked_response")
        assert http_camera.send("test_test") == (ResponseCodeHTTP.OK, "mocked_response")

def test_error_code(http_camera, monkeypatch):
    http_camera.address = ("0.0.12.13", 80)
    with mock.patch('requests.get') as mock_get:
        mock_get.return_value = MockResponse(400, "mocked_response")
        assert http_camera.send("test_test") == (ResponseCodeHTTP.ERROR, None)

def test_wrong_address(http_camera, monkeypatch):
    def mocked_get(command):
        assert command == ('http://0.0.0.0:80/ajaxcom?szCmd=' + 'test_test')

    with mock.patch("requests.get", mocked_get):
        assert http_camera.send("test_test") == (ResponseCodeHTTP.NO_ADDRESS, None)

def test_none_address(http_camera, monkeypatch):
    def mocked_get(command):
        assert command == ('http://0.0.0.0:80/ajaxcom?szCmd=' + 'test_test')

    http_camera.address = None
    with mock.patch("requests.get", mocked_get):
        assert http_camera.send("test_test") == (ResponseCodeHTTP.NO_ADDRESS, None)
