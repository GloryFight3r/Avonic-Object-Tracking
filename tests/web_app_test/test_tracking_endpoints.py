from unittest import mock
import socket
import pytest
import numpy as np
from web_app.integration import GeneralController
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_control_api import CameraSocket
import web_app
from web_app.tracking_endpoints import track_presets, track_continuously

sock = mock.Mock()

@pytest.fixture()
def camera(monkeypatch):
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

    cam_api = CameraAPI(CameraSocket(sock=sock, address=('0.0.0.0', 52381)))
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




def test_track_presets(client):
    rv = client.get('preset/track')
    assert rv.status_code == 200
    assert rv.data == bytes('{"preset":1}\n', "utf-8")

def test_track_continuously(client):
    rv = client.get('calibration/track')
    assert rv.status_code == 200
    assert rv.data == bytes('{"preset":0}\n', "utf-8")

def test_track_continuously_without_adaptive_zooming(client):
    rv = client.get('calibration/track/no/zoom')
    assert rv.status_code == 200 
    assert rv.data == bytes('{"preset":4}\n', "utf-8")