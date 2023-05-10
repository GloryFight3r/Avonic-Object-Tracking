from unittest import mock
import pytest
import socket
from web_app.integration import GeneralController
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_control_api import Camera
from microphone_api.microphone_control_api import MicrophoneAPI
from microphone_api.microphone_adapter import UDPSocket
import web_app
import json

@pytest.fixture()
def camera(monkeypatch):
    def mocked_connect(addr):
        pass

    def mocked_close(self):
        pass

    def mocked_send_all(bytes):
        pass

    def mocked_recv(size):
        return bytes.fromhex("9041FF") 

    sock = socket.socket
    monkeypatch.setattr(sock, "connect", mocked_connect)
    monkeypatch.setattr(sock, "close", mocked_close)
    monkeypatch.setattr(sock, "sendall", mocked_send_all)
    monkeypatch.setattr(sock, "recv", mocked_recv)
    
    cam_api = CameraAPI(Camera(sock, None))
    def mocked_camera_reconnect():
        pass

    monkeypatch.setattr(cam_api.camera, "reconnect", mocked_camera_reconnect)

    return cam_api

@pytest.fixture
def client(camera):
    """A test client for the app."""
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"elevation":90}}}\r\n', "ascii"), None)
    mic_api = MicrophoneAPI(UDPSocket(None, sock))

    cam_api = camera

    test_controller = GeneralController()
    test_controller.load_mock()
    test_controller.set_cam_api(cam_api)
    test_controller.set_mic_api(mic_api)
    app = web_app.create_app(test_controller=test_controller)
    app.config['TESTING'] = True
    return app.test_client()

def test_fail(client):
    """Test an always failing endpoint."""

    rv = client.get('/fail-me')
    assert rv.status_code == 418

def test_turn_on(client):
    """Test a turn on endpoint."""

    rv = client.post('/camera/on')
    assert rv.status_code == 200

def test_turn_off(client):
    """Test a turn off endpoint."""

    rv = client.post('/camera/off')
    assert rv.status_code == 200

def test_reboot(client):
    """Test a reboot endpoint."""

    rv = client.post('/camera/reboot')
    assert rv.status_code == 200

def test_home(client):
    """Test a home endpoint."""

    rv = client.post('/camera/reboot')
    assert rv.status_code == 200

def test_move_absolute(client):
    """Test a move absolute endpoint."""
    req_data = json.dumps({"absolute-speed-x" : 20, "absolute-speed-y" : 10, "absolute-degrees-x" : 40, "absolute-degrees-y" : 15})
    rv = client.post('/camera/move/absolute', data=req_data,  content_type='application/json')
    assert rv.status_code == 200

def test_move_relative(client):
    """Test a move relative endpoint."""
    req_data = json.dumps({"relative-speed-x" : 20, "relative-speed-y" : 10, "relative-degrees-x" : 40, "relative-degrees-y" : 15})
    rv = client.post('/camera/move/relative', data=req_data,  content_type='application/json')
    assert rv.status_code == 200

def test_move_vector(client):
    """Test a move towards a vector endpoint."""
    req_data = json.dumps({"vector-speed-x" : 20, "vector-speed-y" : 10, "vector-x" : 0.5, "vector-y" : 0.5, "vector-z" : 0.5})
    rv = client.post('/camera/move/vector', data=req_data,  content_type='application/json')
    assert rv.status_code == 200

def test_set_zoom(client):
    rv = client.post('/camera/zoom/set', data=json.dumps({"zoomValue" : 20}),  content_type='application/json')
    assert rv.status_code == 200
