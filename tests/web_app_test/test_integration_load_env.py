from unittest import mock
import socket
import json
import pytest
import numpy as np
from web_app.integration import GeneralController
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_control_api import Camera
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import UDPSocket
from avonic_speaker_tracker.preset import PresetCollection
import web_app

sock = mock.Mock()

@pytest.fixture()
def camera(monkeypatch):
    cam_sock = socket.socket
    def mocked_connect(t):
        pass

    def mocked_close():
        pass

    def mocked_send_all(bytes):
        pass

    def mocked_recv(size):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'

    def mocked_timeout(ms):
        pass

    def mocked_socket(a, b):
        return cam_sock

    monkeypatch.setattr(socket, "socket", mocked_socket)
    monkeypatch.setattr(cam_sock, "connect", mocked_connect)
    monkeypatch.setattr(cam_sock, "close", mocked_close)
    monkeypatch.setattr(cam_sock, "sendall", mocked_send_all)
    monkeypatch.setattr(cam_sock, "recv", mocked_recv)
    monkeypatch.setattr(cam_sock, "settimeout", mocked_timeout)

    cam_api = CameraAPI(Camera(cam_sock, (None, 1259)))
    def mocked_camera_reconnect():
        pass
    def mocked_get_zoom():
        return 128
    def mocked_get_direction():
        return np.array([0, 0, 0])

    monkeypatch.setattr(cam_api.camera, "reconnect", mocked_camera_reconnect)
    monkeypatch.setattr(cam_api, "get_zoom", mocked_get_zoom)
    monkeypatch.setattr(cam_api, "get_direction", mocked_get_direction)

    monkeypatch.setenv("CAM_IP", "0.0.0.0")
    monkeypatch.setenv("CAM_PORT", "800")
    monkeypatch.setenv("SERVER_ADDRESS", "0.0.0.0")

    return cam_api


@pytest.fixture
def client(camera):
    """A test client for the app."""
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":0}}}\r\n', "ascii"), None)
    mic_api = MicrophoneAPI(UDPSocket(None, sock))
    mic_api.height = 1

    cam_api = camera

    test_controller = GeneralController()
    test_controller.load_mock()
    test_controller.set_cam_api(cam_api)
    test_controller.set_mic_api(mic_api)
    test_controller.set_preset_collection(PresetCollection(filename=None))
    test_controller.ws = mock.Mock()
    app = web_app.create_app(test_controller=None)
    app.config['TESTING'] = True
    return app.test_client()

def test_load_env(client):
    pass
