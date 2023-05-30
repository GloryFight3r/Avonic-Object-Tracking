import socket
import math
import pytest
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI, degrees_to_command
from avonic_camera_api.camera_adapter import CameraSocket, ResponseCode
from avonic_camera_api import converter


def generate_relative_commands():
    return [
        (1, 1, 30, 0, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x03\x01\x01\x00\x01\x0B\x00\x00\x00\x00\x00\xFF', ResponseCode.ACK),
        (5, 1, 30, 60, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x03\x05\x01\x00\x01\x0B\x00\x00\x03\x06\x00\xFF', ResponseCode.ACK),
        (1, 20, -45, 0, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x03\x01\x14\x0F\x0D\x07\x08\x00\x00\x00\x00\xFF', ResponseCode.ACK),
        (24, 12, 0, -30, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x03\x18\x0C\x00\x00\x00\x00\x0F\x0E\x05\x00\xFF', ResponseCode.ACK),
        (10, 10, 30, 30, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x03\x0A\x0A\x00\x01\x0B\x00\x00\x01\x0B\x00\xFF', ResponseCode.ACK),
    ]


@pytest.fixture()
def camera(monkeypatch):
    def mocked_connect(addr):
        pass

    def mocked_close():
        pass

    def mocked_timeout(ms):
        pass

    sock = socket.socket
    monkeypatch.setattr(sock, "connect", mocked_connect)
    monkeypatch.setattr(sock, "close", mocked_close)
    monkeypatch.setattr(sock, "settimeout", mocked_timeout)

    return CameraAPI(CameraSocket(sock=sock, address=('0.0.0.0', 52382)))


@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta, expected, expected2", generate_relative_commands())
def test_move_relative(monkeypatch, camera: CameraAPI, speed_alpha, speed_beta, alpha, beta, expected, expected2):
    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'
    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)

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


@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta",
    generate_relative_commands_bad_parameters())
def test_move_relative_bad_parameters(camera:CameraAPI,
    speed_alpha, speed_beta, alpha, beta):
    with pytest.raises (AssertionError):
        camera.move_relative(speed_alpha, speed_beta, alpha, beta)


@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta",
    generate_relative_commands_bad_parameters())
def test_move_absolute_bad_parameters(camera:CameraAPI,
    speed_alpha, speed_beta, alpha, beta):
    with pytest.raises (AssertionError):
        camera.move_absolute(speed_alpha, speed_beta, alpha, beta)


def generate_degrees_to_commands():
    return [
        # positive degrees tests
        (45, "00020808"),
        (60, "00030600"),
        (90, "00050100"),
        (170, "00090900"),
        # negative degrees tests
        (-45, "0f0d0708"),
        (-60, "0f0c0a00"),
        (-90, "0f0a0f00"),
        (-170, "0f060700"),
        # decimal degrees tests
        (13.5, "00000c02"),
        (13.9, "00000c08"),
        (-22.6, "0f0e0b0b"),
        (-10.12, "0f0f060f"),
    ]


@pytest.mark.parametrize("alpha, expected", generate_degrees_to_commands())
def test_degrees_to_command(alpha, expected):
    assert degrees_to_command(alpha) == expected


def generate_absolute_commands():
    return [
        (1, 1, 30, 0, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x02\x01\x01\x00\x01\x0B\x00\x00\x00\x00\x00\xFF', ResponseCode.ACK),
        (5, 1, 30, 60, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x02\x05\x01\x00\x01\x0B\x00\x00\x03\x06\x00\xFF', ResponseCode.ACK),
        (1, 20, -45, 0, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x02\x01\x14\x0F\x0D\x07\x08\x00\x00\x00\x00\xFF', ResponseCode.ACK),
        (24, 12, 0, -30, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x02\x18\x0C\x00\x00\x00\x00\x0F\x0E\x05\x00\xFF', ResponseCode.ACK),
        (10, 10, 30, 30, b'\x01\x00\x00\x0F\x00\x00\x00\x01\x81\x01\x06\x02\x0A\x0A\x00\x01\x0B\x00\x00\x01\x0B\x00\xFF', ResponseCode.ACK),
    ]


@pytest.mark.parametrize("speed_alpha, speed_beta, alpha, beta, expected, expected2",
     generate_absolute_commands())
def test_move_absolute(monkeypatch, camera,
    speed_alpha, speed_beta, alpha, beta, expected, expected2):
    def mocked_send(message):
        print(message, expected)
        assert message == expected
    def mocked_return(bytes_receive):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'
    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)

    assert camera.move_absolute(speed_alpha, speed_beta, alpha, beta) == expected2


def test_home_commands(monkeypatch, camera):
    expected2 = ResponseCode.ACK
    expected = b'\x01\x00\x00\x05\x00\x00\x00\x01\x81\x01\x06\x04\xff'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'
    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)

    assert camera.home() == expected2


def test_reboot_command(monkeypatch, camera):
    expected2 = ResponseCode.COMPLETION
    expected = b'\x01\x00\x00\x06\x00\x00\x00\x01\x81\x0A\x01\x06\x01\xff'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return None
    def mocked_connect(address):
        pass
    def mocked_timeout(ms: float):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "connect", mocked_connect)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)

    assert camera.reboot(camera.camera.sock) == expected2


def test_stop_command(monkeypatch, camera):
    expected2 = ResponseCode.ACK
    expected = b'\x01\x00\x00\x09\x00\x00\x00\x01\x81\x01\x06\x01\x05\x05\x03\x03\xff'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'
    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)

    assert camera.stop() == expected2


def test_turn_on_command(monkeypatch, camera):
    expected2 = ResponseCode.ACK
    expected = b'\x01\x00\x00\x06\x00\x00\x00\x01\x81\x01\x04\x00\x02\xff'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'
    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)

    assert camera.turn_on() == expected2


def test_turn_off_command(monkeypatch, camera):
    expected2 = ResponseCode.ACK
    expected = b'\x01\x00\x00\x06\x00\x00\x00\x01\x81\x01\x04\x00\x03\xff'

    def mocked_send(message):
        assert message == expected
    def mocked_return(bytes_receive):
        return b'\x01\x00\x00\x00\x00\x00\x00\x01\x90\x41\xff'

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)

    assert camera.turn_off() == expected2


def generate_get_direction_commands():
    return [
        ([0, 0], b'\x01\x00\x00\x05\x00\x00\x00\x01\x90\x50\x00\x00\x00\x00\x00\x00\x00\x00\xFF'),
        ([1, 1], b'\x01\x00\x00\x05\x00\x00\x00\x01\x90\x50\x00\x00\x00\x01\x00\x00\x00\x01\xFF'),
        ([1, 700], b'\x01\x00\x00\x05\x00\x00\x00\x01\x90\x50\x00\x00\x00\x01\x00\x02\x0B\x0C\xFF'),
        ([-2448, -443], b'\x01\x00\x00\x05\x00\x00\x00\x01\x90\x50\x0F\x06\x07\x00\x0F\x0E\x04\x05\xFF'),
    ]


@pytest.mark.parametrize("direction, ret_msg", generate_get_direction_commands())
def test_get_direction(monkeypatch, camera, direction, ret_msg):
    expected_msg = b'\x01\x00\x00\x05\x00\x00\x00\x01\x81\x09\x06\x12\xFF'

    def mocked_send(message):
        assert message == expected_msg
    def mocked_return(bytes_receive):
        return ret_msg
    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)
    direction = np.array(direction) * (5/72) / 180 * math.pi
    assert (camera.get_direction() == converter.angle_vector(direction[0], direction[1])).all()


def test_camera_error(monkeypatch, camera):
    expected_msg = b'\x01\x00\x00\x05\x00\x00\x00\x01\x81\x09\x06\x12\xFF'

    def mocked_send(message):
        assert message == expected_msg
    def mocked_return(bytes_receive):
        raise TimeoutError
    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)
    assert camera.get_direction() == ResponseCode.TIMED_OUT


def test_camera_error_second(monkeypatch, camera):
    expected_msg = b'\x01\x00\x00\x05\x00\x00\x00\x01\x81\x09\x06\x12\xFF'
    camera.camera.counter = 0
    def mocked_send(message):
        assert message == expected_msg
    def mocked_return(bytes_receive):
        camera.camera.counter += 1
        if camera.camera.counter == 1:
            return b'\x01\x00\x00\x05\x00\x00\x00\x01\x51\x51\x00\x00\x00\x00\x00\x00\x00\x00\xFF'
        raise TimeoutError

    def mocked_timeout(ms):
        pass

    monkeypatch.setattr(camera.camera.sock, "sendall", mocked_send)
    monkeypatch.setattr(camera.camera.sock, "recv", mocked_return)
    monkeypatch.setattr(camera.camera.sock, "settimeout", mocked_timeout)
    assert camera.get_direction() == ResponseCode.TIMED_OUT


def test_send_no_address(monkeypatch, camera):
    camera.camera.address = None
    assert camera.get_direction() == ResponseCode.NO_ADDRESS


def test_reconnect_no_new_address(monkeypatch, camera):
    camera.camera.address = None
    assert camera.reboot(camera.camera.sock) == ResponseCode.NO_ADDRESS


@pytest.fixture()
def camera_no_address(monkeypatch):
    def mocked_connect(addr):
        pass

    def mocked_close():
        pass

    def mocked_timeout(ms):
        pass

    sock = socket.socket
    monkeypatch.setattr(sock, "connect", mocked_connect)
    monkeypatch.setattr(sock, "close", mocked_close)
    monkeypatch.setattr(sock, "settimeout", mocked_timeout)

    return CameraAPI(CameraSocket(sock=sock))


def test_init_no_address(monkeypatch, camera_no_address):
    assert camera_no_address.camera.address is None


def test_reconnect_new_address(monkeypatch, camera_no_address):
    assert camera_no_address.set_address(camera_no_address.camera.sock, ('0.0.0.0', 52381))\
           == ResponseCode.COMPLETION


def test_reconnect_new_address_timeout(monkeypatch, camera_no_address):
    def mocked_return(bytes_receive):
        raise TimeoutError

    monkeypatch.setattr(camera_no_address.camera.sock, "connect", mocked_return)
    assert camera_no_address.set_address(camera_no_address.camera.sock, ('0.0.0.0', 52381)) \
           == ResponseCode.TIMED_OUT


def test_new_address_no_address(monkeypatch, camera_no_address):
    assert camera_no_address.set_address(camera_no_address.camera.sock) == ResponseCode.NO_ADDRESS
