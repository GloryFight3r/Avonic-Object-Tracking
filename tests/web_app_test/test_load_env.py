from unittest import mock
import socket
import time
import pytest
import numpy as np
import time
from web_app.integration import GeneralController, close_running_threads
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_control_api import CameraSocket
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import MicrophoneSocket
import web_app

sock = mock.Mock()

@pytest.fixture()
def camera(monkeypatch):
    cam_sock = socket.socket
    def mocked_connect(t, self=None):
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

    cam_api = CameraAPI(CameraSocket(cam_sock, (None, 1259)))
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

test_controller = GeneralController()

@pytest.fixture
def client(camera):
    """A test client for the app."""
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":0}}}\r\n', "ascii"), None)
    mic_api = MicrophoneAPI(MicrophoneSocket(None, sock))
    mic_api.height = 1

    cam_api = camera

    test_controller.load_env()
    test_controller.ws = mock.Mock()
    app = web_app.create_app(test_controller=test_controller)
    app.config['TESTING'] = True
    return app.test_client()

def test_load_env(client):
    time.sleep(0.5)
    test_controller.footage_thread_event.set()
    test_controller.info_threads_break.value = 1
