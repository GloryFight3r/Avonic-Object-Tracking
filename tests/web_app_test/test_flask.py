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
    def mocked_connect(addr):
        pass

    def mocked_close(self):
        pass

    def mocked_send_all(bytes):
        pass

    def mocked_recv(size):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'

    def mocked_timeout(ms):
        pass

    sock = socket.socket
    monkeypatch.setattr(sock, "connect", mocked_connect)
    monkeypatch.setattr(sock, "close", mocked_close)
    monkeypatch.setattr(sock, "sendall", mocked_send_all)
    monkeypatch.setattr(sock, "recv", mocked_recv)
    monkeypatch.setattr(sock, "settimeout", mocked_timeout)

    cam_api = CameraAPI(Camera(sock, (None, 1259)))
    def mocked_camera_reconnect():
        pass
    def mocked_get_zoom():
        return 128
    def mocked_get_direction():
        return np.array([0, 0, 0])

    monkeypatch.setattr(cam_api.camera, "reconnect", mocked_camera_reconnect)
    monkeypatch.setattr(cam_api, "get_zoom", mocked_get_zoom)
    monkeypatch.setattr(cam_api, "get_direction", mocked_get_direction)

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

    rv = client.post('/camera/move/home')
    assert rv.status_code == 200


def test_move_absolute(client):
    """Test a move absolute endpoint."""
    req_data = {"absolute-speed-x": 20, "absolute-speed-y": 10,
        "absolute-degrees-x": 40, "absolute-degrees-y": 15}
    rv = client.post('/camera/move/absolute', data=req_data)
    assert rv.status_code == 200


def test_bad_move_absolute(client):
    """Test a move absolute endpoint."""
    req_data = {"absolute-speed-x": 30, "absolute-speed-y": 10,
        "absolute-degrees-x": 40, "absolute-degrees-y": 15}
    rv = client.post('/camera/move/absolute', data=req_data)
    assert rv.status_code == 400


def test_move_relative(client):
    """Test a move relative endpoint."""
    req_data = {"relative-speed-x": 20, "relative-speed-y": 10,
        "relative-degrees-x": 40, "relative-degrees-y": 15}
    rv = client.post('/camera/move/relative', data=req_data)
    assert rv.status_code == 200


def test_move_vector(client):
    """Test a move towards a vector endpoint."""
    req_data = {"vector-speed-x": 20, "vector-speed-y": 10,
        "vector-x": 0.5, "vector-y": 0.5, "vector-z": 0.5}
    rv = client.post('/camera/move/vector', data=req_data)
    assert rv.status_code == 200


def bad_move_vector(client):
    """Test a move towards a vector endpoint."""
    req_data = {"vector-speed-x": 20, "vector-speed-y": 10,
        "vector-x": 0.5, "vector-y": 0.5, "vector-z": 0.5}
    rv = client.post('/camera/move/vector', data=req_data)
    assert rv.status_code == 400


def test_bad_move_relative(client):
    """Test a move relative endpoint."""
    req_data = {"relative-speed-x": 30, "relative-speed-y": 10,
        "relative-degrees-x": 40, "relative-degrees-y": 15}
    rv = client.post('/camera/move/relative', data=req_data)
    assert rv.status_code == 400


def test_set_zoom(client):
    rv = client.post('/camera/zoom/set', data={"zoom-value" : 0})
    assert rv.status_code == 200


def test_bad_lower_bound_set_zoom(client):
    rv = client.post('/camera/zoom/set', data={"zoom-value" : -1})
    assert rv.status_code == 400


def test_bad_upper_bound_set_zoom(client):
    rv = client.post('/camera/zoom/set', data={"zoom-value" : 16385})
    assert rv.status_code == 400


def test_upper_bound_set_zoom(client):
    rv = client.post('/camera/zoom/set', data=dict({"zoom-value" : 16384}))
    assert rv.status_code == 200


def test_move_stop_camera(client):
    rv = client.post('/camera/move/stop')
    assert rv.status_code == 200


def test_get_zoom(client):
    rv = client.get('/camera/zoom/get')
    assert rv.status_code == 200 and rv.data == bytes("{\"zoom-value\":128}\n", "utf-8")

def test_set_microphone_height(client):
    rv = client.post('/microphone/height/set', data={"microphone-height": 1.7})
    assert rv.status_code == 200 and rv.data == bytes("{\"microphone-height\":1.7}\n", "utf-8")


def test_get_microphone_direction(client):
    rv = client.get('microphone/direction')
    res_vec = json.loads(rv.data)["microphone-direction"]
    assert rv.status_code == 200 and np.allclose(res_vec, [0.0, 0.0, 1.0])


def test_add_direction_to_mic(client):
    client.get('/calibration/reset')
    rv = client.get('/calibration/add_direction_to_mic')
    assert rv.status_code == 200


def test_add_direction_to_speaker(client):
    rv = client.get('/calibration/add_directions_to_speaker')
    assert rv.status_code == 200


def test_calibration_reset(client):
    rv = client.get('/calibration/reset')
    assert rv.status_code == 200


def test_calibration_is_set(client):
    rv = client.get('/calibration/is_set')
    assert rv.status_code == 200 \
        and rv.data == bytes("{\"is_set\":false}\n", "utf-8")

def test_calibration_get_camera(client):
    rv = client.get('/calibration/camera')
    assert rv.status_code == 200 \
        and rv.data == bytes("{\"camera-coords\":[0.0,0.0,0.0]}\n", "utf-8")

def test_update_microphone(client):
    rv = client.post('/update/microphone', json=json.dumps({"test": "testington"}))
    assert rv.status_code == 200


def test_update_camera(client):
    rv = client.post('/update/camera', json=json.dumps({"test": "testington"}))
    assert rv.status_code == 200


def test_update_calibration(client):
    rv = client.post('/update/calibration', json=json.dumps({"test": "testington"}))
    assert rv.status_code == 200


def test_thread(client):
    rv = client.post('/thread/start')
    assert rv.status_code == 200
    rv = client.get('/thread/running')
    assert rv.status_code == 200 and rv.data == bytes("{\"is-running\":true}\n", "utf-8")
    rv = client.post('/thread/stop')
    assert rv.status_code == 200
    rv = client.get('/thread/running')
    assert rv.status_code == 200 and rv.data == bytes("{\"is-running\":false}\n", "utf-8")
    rv = client.post('/thread/start')
    assert rv.status_code == 200
    rv = client.get('/thread/running')
    assert rv.status_code == 200 and rv.data == bytes("{\"is-running\":true}\n", "utf-8")
    rv = client.post('/thread/start')
    assert rv.status_code == 403
    rv = client.post('/thread/stop')
    assert rv.status_code == 200


def test_is_speaking(client):
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"in1":{"peak":-55}}}\r\n', "ascii"), None)
    rv = client.get('/microphone/speaking')
    assert rv.status_code == 200 and rv.data == bytes("{\"microphone-speaking\":false}\n", "utf-8")
    sock.recvfrom.return_value = \
        (bytes('{"m":{"in1":{"peak":-54}}}\r\n', "ascii"), None)
    rv = client.get('/microphone/speaking')
    assert rv.status_code == 200 and rv.data == bytes("{\"microphone-speaking\":true}\n", "utf-8")
    sock.recvfrom.return_value = \
        (bytes('{"m":{"in1":{"peak":-100}}}\r\n', "ascii"), None)
    rv = client.get('/microphone/speaking')
    assert rv.status_code == 200 and rv.data == bytes("{\"microphone-speaking\":true}\n", "utf-8")


def test_add_preset_location(client):
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0,
            "preset-name": "test-preset-name"
        }
    )
    assert rv.status_code == 200
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0,
            "preset-name": "test-preset-name"
        }
    )
    assert rv.status_code == 400
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "preset-name": "test-preset-name"
        }
    )
    assert rv.status_code == 400
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-z" : 0,
            "preset-name": "test-preset-name-y-missing"
        }
    )
    assert rv.status_code == 400
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0,
            "preset-name": "test-preset-name-x-missing"
        }
    )
    assert rv.status_code == 400
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0,
            "preset-name": "test-preset-name-z-missing"
        }
    )
    assert rv.status_code == 400
    rv = client.post("preset/add",
        data={
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0,
            "preset-name": "test-preset-name-alpha-missing"
        }
    )
    assert rv.status_code == 400
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0
        }
    )
    assert rv.status_code == 400


def test_edit_preset_location(client):
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0.25,
            "camera-direction-beta" : 0.25,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : -1,
            "preset-name": "test-another-preset-name"
        }
    )
    assert rv.status_code == 200
    rv = client.post("preset/edit",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0,
            "preset-name": "test-wrong-preset-name"
        }
    )
    assert rv.status_code == 400
    rv = client.post("preset/edit",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 0,
            "mic-direction-y" : 1,
            "mic-direction-z" : 0,
            "preset-name": "test-another-preset-name"
        }
    )
    assert rv.status_code == 200


def test_get_preset_list(client):
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 0,
            "mic-direction-x" : 1,
            "mic-direction-y" : 0,
            "mic-direction-z" : 0,
            "preset-name": "test-preset-name"
        }
    )
    assert rv.status_code == 200
    rv = client.post("preset/add",
        data={
            "camera-direction-alpha" : 0,
            "camera-direction-beta" : 0,
            "camera-zoom-value": 1,
            "mic-direction-x" : 0,
            "mic-direction-y" : 1,
            "mic-direction-z" : 0,
            "preset-name": "test-another-preset-name"
        }
    )
    assert rv.status_code == 200
    rv = client.get("preset/get_list")
    assert rv.status_code == 200\
        and rv.data == bytes("{\"preset-list\":[\"test-preset-name\","\
            + "\"test-another-preset-name\"]}\n", "utf-8")
    sock.recvfrom.return_value = \
        (bytes('{"m":{"in1":{"peak":-54}}}\r\n', "ascii"), None)
    rv = client.post("preset/point")
    assert rv.status_code == 200
    rv = client.get("preset/info/test-non-existent-preset-name")
    assert rv.status_code == 400
    rv = client.get("preset/info/test-preset-name")
    assert rv.status_code == 200 and bytes("{" \
            + "\"camera-direction-alpha\":0," \
            + "\"camera-direction-beta\":0," \
            + "\"camera-direction-value\":0," \
            + "\"mic-direction-x\":1," \
            + "\"mic-direction-y\":0," \
            + "\"mic-direction-z\":0," \
            + "\"preset-name\":\"test-preset-name\"}\n", "utf-8")
    rv = client.get("preset/info/test-another-preset-name")
    assert rv.status_code == 200 and bytes("{" \
            + "\"camera-direction-alpha\":0," \
            + "\"camera-direction-beta\":0," \
            + "\"camera-direction-value\":0," \
            + "\"mic-direction-x\":0," \
            + "\"mic-direction-y\":1," \
            + "\"mic-direction-z\":0," \
            + "\"preset-name\":\"test-another-preset-name\"}\n", "utf-8")
    rv = client.post("preset/remove",
    data={"preset-name" : "test-non-existent-preset-name"})
    assert rv.status_code == 400
    rv = client.post("preset/remove",
    data={"preset-name" : "test-another-preset-name"})
    assert rv.status_code == 200
    rv = client.post("preset/remove",
    data={"preset-name" : "test-another-preset-name"})
    assert rv.status_code == 400
    rv = client.get("preset/info/test-another-preset-name")
    assert rv.status_code == 400
    rv = client.get("preset/get_list")
    assert rv.status_code == 200\
        and rv.data == bytes("{\"preset-list\":[\"test-preset-name\"]}\n", "utf-8")
    rv = client.post("preset/remove",
    data={"preset-name" : "test-preset-name"})
    assert rv.status_code == 200
    rv = client.get("preset/get_list")
    assert rv.status_code == 200 and rv.data == bytes("{\"preset-list\":[]}\n", "utf-8")
    rv = client.get("preset/info/test-preset-name")
    assert rv.status_code == 400
