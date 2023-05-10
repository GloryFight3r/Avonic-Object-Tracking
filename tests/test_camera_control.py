import pytest
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.camera_adapter import Camera
import socket
import numpy as np

def generate_relative_commands():
    return [
        (1, 1, 30, 0, b'\x81\x01\x06\x03\x01\x01\x00\x01\x0E\x00\x00\x00\x00\x00\xFF\x9b', b'9041FF'),
        (5, 1, 30, 60, b'\x81\x01\x06\x03\x05\x01\x00\x01\x0E\x00\x00\x03\x0C\x00\xFF\xae', b'9041FF'),
        (1, 20, -45, 0, b'\x81\x01\x06\x03\x01\x14\x0F\x0D\x03\x00\x00\x00\x00\x00\xFF\xbe', b'9041FF'),
        (24, 12, 0, -30, b'\x81\x01\x06\x03\x18\x0C\x00\x00\x00\x00\x0F\x0E\x02\x00\xFF\xcd', b'9041FF'),
        (10, 10, 30, 30, b'\x81\x01\x06\x03\x0A\x0A\x00\x01\x0E\x00\x00\x01\x0E\x00\xFF\xbc', b'9041FF'),
    ]

@pytest.fixture()
def camera(monkeypatch):
    def mocked_connect(addr):
        pass

    def mocked_close():
        pass

    sock = socket.socket
    monkeypatch.setattr(sock, "connect", mocked_connect)
    monkeypatch.setattr(sock, "close", mocked_close)

    return CameraAPI(Camera(sock, None))

@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta, expected, expected2", generate_relative_commands())
def test_move_relative(monkeypatch, camera:CameraAPI, speed_alpha, speed_beta, alpha, beta, expected, expected2):
    def mocked_sned(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return bytes.fromhex("9041FF")

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_sned)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)

    assert camera.move_relative(speed_alpha, speed_beta, alpha, beta) == expected2

def generate_relative_commands_bad_parameters():
    return [
        (11, 10, 150, 91),
        (11, 10, 180, 30),
        (23, 21, 30, 30),
        (0, 3, 30, 30),
        (1, 0, 30, 30),
        (3, 3, -171, 10),
        (3, 3, 5, -31)
    ]

@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta", generate_relative_commands_bad_parameters())
def test_move_relative_bad_parameters(monkeypatch, camera:CameraAPI, speed_alpha, speed_beta, alpha, beta):
    with pytest.raises (AssertionError):
        camera.move_relative(speed_alpha, speed_beta, alpha, beta)

@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta", generate_relative_commands_bad_parameters())
def test_move_absolute_bad_parameters(monkeypatch, camera:CameraAPI, speed_alpha, speed_beta, alpha, beta):
    with pytest.raises (AssertionError):
        camera.move_absolute(speed_alpha, speed_beta, alpha, beta)

def generate_degrees_to_commands():
    return [
        # positive degrees tests
        (45, "00020d00"),
        (60, "00030c00"),
        (90, "00050a00"),
        (170, "000a0a00"),
        # negative degrees tests
        (-45, "0f0d0300"),
        (-60, "0f0c0400"),
        (-90, "0f0a0600"),
        (-170, "0f050600"),
        # decimal degrees tests
        (13.5, "00000d08"),
        (13.9, "00000d0e"),
        (-22.6, "0f0e0907"),
        (-10.12, "0f0f050f"),
    ]

@pytest.mark.parametrize("alpha, expected", generate_degrees_to_commands())
def test_degrees_to_command(camera:CameraAPI, alpha, expected):
    assert camera.degrees_to_command(alpha) == expected

def generate_absolute_commands():
    return [
        (1, 1, 30, 0, b'\x81\x01\x06\x02\x01\x01\x00\x01\x0E\x00\x00\x00\x00\x00\xFF\x9a', b'9041FF'),
        (5, 1, 30, 60, b'\x81\x01\x06\x02\x05\x01\x00\x01\x0E\x00\x00\x03\x0C\x00\xFF\xad', b'9041FF'),
        (1, 20, -45, 0, b'\x81\x01\x06\x02\x01\x14\x0F\x0D\x03\x00\x00\x00\x00\x00\xFF\xbd', b'9041FF'),
        (24, 12, 0, -30, b'\x81\x01\x06\x02\x18\x0C\x00\x00\x00\x00\x0F\x0E\x02\x00\xFF\xcc', b'9041FF'),
        (10, 10, 30, 30, b'\x81\x01\x06\x02\x0A\x0A\x00\x01\x0E\x00\x00\x01\x0E\x00\xFF\xbb', b'9041FF'),
    ]

@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta, expected, expected2", generate_absolute_commands())
def test_move_absolute(monkeypatch, camera, speed_alpha, speed_beta, alpha, beta, expected, expected2):
    def mocked_send(message):
        print(message, expected)
        assert message == expected
    def mocked_return(bytes_receive):
        return bytes.fromhex("9041FF")

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)

    assert camera.move_absolute(speed_alpha, speed_beta, alpha, beta) == expected2

def test_home_commands(monkeypatch, camera):
    expected2 = b'9041FF'
    expected = b'\x81\x01\x06\x04\xff\x8b'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return bytes.fromhex("9041FF")

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)

    assert camera.home() == expected2

def test_reboot_command(monkeypatch, camera):
    expected2 = None
    expected = b'\x81\x0A\x01\x06\x01\xff\x92'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return None
    def mocked_connect():
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera, "reconnect", mocked_connect)

    assert camera.reboot() == expected2

def test_stop_command(monkeypatch, camera):
    expected2 = b'9041FF'
    expected = b'\x81\x01\x06\x01\x05\x05\x03\x03\xff\x98'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return bytes.fromhex("9041FF")

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)

    assert camera.stop() == expected2

def test_turn_on_command(monkeypatch, camera):
    expected2 = b'9041FF'
    expected = b'\x81\x01\x04\x00\x02\xff\x87'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return bytes.fromhex("9041FF")

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)

    assert camera.turn_on() == expected2

def test_turn_off_command(monkeypatch, camera):
    expected2 = b'9041FF'
    expected = b'\x81\x01\x04\x00\x03\xff\x88'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return bytes.fromhex("9041FF")

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)

    assert camera.turn_off() == expected2

def generate_get_direction_commands():
    return [
        ([0, 0], b'\x90\x50\x00\x00\x00\x00\x00\x00\x00\x00\xFF'),
        ([1, 1], b'\x90\x50\x00\x00\x00\x01\x00\x00\x00\x01\xFF'),
        ([700, 1], b'\x90\x50\x00\x02\x0B\x0C\x00\x00\x00\x01\xFF'),
        ([1, 700], b'\x90\x50\x00\x00\x00\x01\x00\x02\x0B\x0C\xFF'),
        ([-2447, -442], b'\x90\x50\x0F\x06\x07\x00\x0F\x0E\x04\x05\xFF'),
    ]

@pytest.mark.parametrize("direction, ret_msg", generate_get_direction_commands())
def test_get_direction(monkeypatch, camera, direction, ret_msg):
    expected_msg = b'\x81\x09\x06\x12\xFF'

    def mocked_send(message):
        assert message.startswith(expected_msg)
    def mocked_return(bytes_receive):
        return ret_msg

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    assert (camera.get_direction() == np.array(direction)).all()
