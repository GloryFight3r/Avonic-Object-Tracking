import json
from unittest import mock
from avonic_camera_api.footage import FootageThread
import pytest
import socket
import web_app
import numpy as np
from web_app.camera_endpoints import responses
from avonic_camera_api.camera_control_api import ResponseCode
from web_app.integration import GeneralController
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_control_api import CameraSocket
from avonic_speaker_tracker.utils import camera_navigation_utils
import avonic_speaker_tracker.utils.camera_navigation_utils

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
        return np.array([2, 3, 5])
    def mocked_turn_on():
        return ResponseCode.CANCELED
    def mocked_turn_off():
        return ResponseCode.CANCELED
    def mocked_get_zoom():
        return ResponseCode.CANCELED
    def mocked_get_position():
        return ResponseCode.CANCELED
    #def mocked_move(a,b,c):
    #    assert a<20

    monkeypatch.setattr(cam_api, "get_zoom", mocked_get_zoom)
    monkeypatch.setattr(cam_api, "get_direction", mocked_get_direction)
    monkeypatch.setattr(cam_api, "turn_on", mocked_turn_on)
    monkeypatch.setattr(cam_api, "turn_off", mocked_turn_off)
    monkeypatch.setattr(cam_api, "get_zoom", mocked_get_zoom)

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
    #test_controller.footage_thread = FootageThread(None, None)

    app = web_app.create_app(test_controller=test_controller)
    app.config['TESTING'] = True

    return app.test_client()

def test_get_camera_direction(client):
    rv = client.get('camera/position/get')
    assert rv.status_code == 200 
    assert rv.data == bytes('{"position-alpha-value":-0.3805063771123649,"position-beta-value":0.5082672461712843}\n','utf-8')
    
def test_camera_turn_on_bad_weather(client):
    rv = client.post('camera/on')
    assert rv.status_code == 409

def test_camera_turn_off_bad_weather(client):
    rv = client.post('camera/off')
    assert rv.status_code == 409

def test_move_vector_bad_weather(client):
    data = {
        "vector-speed-x" : 25,
        "vector-speed-y" : 20,
        "vector-x" : 1,
        "vector-y" : 1,
        "vector-z" : 1
    }
    rv = client.post('camera/move/vector',data = data)
    assert rv.status_code == 400
    assert rv.data == bytes('{"message":""}\n','utf-8')

def test_get_zoom_bad_weather(client):
    rv = client.get('camera/zoom/get')
    assert rv.status_code == 409

def generate_navigate_tests():
    return [
        (0.5, 0.8, 1920*0.5, 1080*0.8),
        (0.12, 1, 1920*0.5, 1080*1),
        (0.23, 0.4, 1920*0.23, 1080*0.4),
        (0, 0.4, 1920*0, 1080*0.4)
    ]

@pytest.mark.parametrize("x, y, exp_x, exp_y", generate_navigate_tests())
def test_navigate(client, x, y, exp_x, exp_y, monkeypatch):
    data = {
        "x-pos" : x,
        "y-pos" : y
    }
    def mocked_get_fov(xx):
        return np.array([60.38, 35.80])

    def mocked_move_relative(zzz, xx, yy, zz, gg):
        return ResponseCode.ACK
    monkeypatch.setattr(CameraAPI, "calculate_fov", mocked_get_fov)

    monkeypatch.setattr(CameraAPI, "move_relative", mocked_move_relative)
    rv = client.post('navigate/camera',data = data)

    assert rv.status_code == 200

def generate_bad_weather_navigate_tests():
    return [
        (0.5, 1.1),
        (1.5, 0.8),
        (0.5, -1),
        (-1, 0.2)
    ]

@pytest.mark.parametrize("x, y", generate_bad_weather_navigate_tests())
def test_navigate_bad_weather(client, x, y, monkeypatch):
    data = {
        "x-pos" : 1.1,
        "y-pos" : 0.2,
    }
    def mocked_get_fov(xx):
        return np.array([60.38, 35.80])

    def mocked_move_relative(zzz, xx, yy, zz, gg):
        return ResponseCode.ACK
    monkeypatch.setattr(CameraAPI, "calculate_fov", mocked_get_fov)

    monkeypatch.setattr(CameraAPI, "move_relative", mocked_move_relative)
    rv = client.post('navigate/camera',data = data)
    assert rv.status_code == 400


def test_ack_response_code():
    result = responses()[ResponseCode.ACK]
    assert result[0] == json.dumps({"message": "Command accepted"}) and result[1] == 200

def test_completion_response_code():
    result = responses()[ResponseCode.COMPLETION]
    assert result[0] == json.dumps({"message": "Command executed"}) and result[1] == 200

def test_syntax_error_response_code():
    result = responses()[ResponseCode.SYNTAX_ERROR]
    assert result[0] == json.dumps({"message": "Syntax error"}) and result[1] == 400

def test_buffer_full_response_code():
    result = responses()[ResponseCode.BUFFER_FULL]
    assert result[0] == json.dumps({"message": "Command buffer full"}) and result[1] == 400

def test_cancelled_response_code():
    result = responses()[ResponseCode.CANCELED]
    assert result[0] == json.dumps({"message": "Command canceled"}) and result[1] == 409

def test_no_socket_response_code():
    result = responses()[ResponseCode.NO_SOCKET]
    assert result[0] == json.dumps({"message": "No such socket"}) and result[1] == 400

def test_not_executable_response_code():
    result = responses()[ResponseCode.NOT_EXECUTABLE]
    assert result[0] == json.dumps({"message": "Command cannot be executed"}) and result[1] == 400

def test_timed_out_response_code():
    result = responses()[ResponseCode.TIMED_OUT]
    assert result[0] == json.dumps({"message": "Camera timed out"}) and result[1] == 504

def test_no_address_response_code():
    result = responses()[ResponseCode.NO_ADDRESS]
    assert result[0] == json.dumps({"message": "Camera address not specified"}) and result[1] == 400
