from unittest import mock
import socket
from avonic_camera_api.camera_http_request import CameraHTTP
import pytest
import numpy as np
from web_app.integration import GeneralController
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_control_api import CameraSocket
import web_app

sock = mock.Mock()

@pytest.fixture
def mocked_cam_http():
    mocked_cam_http = CameraHTTP(("", 1))

    return mocked_cam_http

@pytest.fixture()
def camera(monkeypatch, mocked_cam_http):
    def mocked_connect(addr, self=None):
        pass

    def mocked_close(self):
        pass

    def mocked_send_all(bytes):
        pass

    def mocked_recv(size):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'

    def mocked_timeout(ms, self=None):
        pass

    sock = socket.socket
    monkeypatch.setattr(sock, "connect", mocked_connect)
    monkeypatch.setattr(sock, "close", mocked_close)
    monkeypatch.setattr(sock, "sendall", mocked_send_all)
    monkeypatch.setattr(sock, "recv", mocked_recv)
    monkeypatch.setattr(sock, "settimeout", mocked_timeout)

    cam_api = CameraAPI(CameraSocket(sock=sock, address=('0.0.0.0', 52381)), mocked_cam_http)
    def mocked_get_zoom():
        return 128
    def mocked_get_direction():
        return np.array([0, 0, 0])

    monkeypatch.setattr(cam_api, "get_zoom", mocked_get_zoom)
    monkeypatch.setattr(cam_api, "get_direction", mocked_get_direction)

    return cam_api

mic_api = mock.Mock()

@pytest.fixture
def client(camera, monkeypatch):
    """A test client for the app."""
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":0}}}\r\n', "ascii"), None)

    mic_api.height = 1

    cam_api = camera

    test_controller = GeneralController()
    test_controller.cam_sock = camera.camera.sock
    test_controller.load_mock()
    test_controller.set_cam_api(cam_api)
    test_controller.set_mic_api(mic_api)
    test_controller.ws = mock.Mock()

    app = web_app.create_app(test_controller=test_controller)
    app.config['TESTING'] = True

    return app.test_client()

def test_address_set_microphone_endpoint_bad_weather(client):
    mic_api.set_address.return_value = ("msg", None)
    data = {
        "ip": "0.0.0.1",
        "port": 1234
    }
    rv = client.post('/microphone/address/set', data=data)
    assert rv.status_code == 400

def test_direction_get_microphone_endpoint_bad_weather(client):
    mic_api.get_direction.return_value = \
        "Unable to get direction from microphone, response was: 404"
    rv = client.get('microphone/direction')
    assert rv.status_code == 504

def test_direction_is_speaking_endpoint_bad_weather(client):
    mic_api.is_speaking.return_value = "Unable to get peak loudness, response was: 404"
    rv = client.get('microphone/speaking')
    assert rv.status_code == 504

def test_get_speaker_direction_endpoint_good_weather(client):
    mic_api.get_direction.return_value = bytes('', "utf-8")
    rv = client.get('microphone/speaker/direction')
    assert rv.status_code == 200
    assert rv.data == bytes('{"microphone-direction":[]}\n',"utf-8")


def test_get_speaker_direction_endpoint_bad_weather(client):
    mic_api.get_direction.return_value = "error"
    rv = client.get('microphone/speaker/direction')
    assert rv.status_code == 504
