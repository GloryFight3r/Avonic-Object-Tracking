from unittest import mock
import pytest
from hypothesis import given, strategies as st
import numpy as np
from microphone_api.microphone_adapter import UDPSocket
from microphone_api.microphone_control_api import MicrophoneAPI


def test_set_height_api():
    mic = UDPSocket(None)
    api = MicrophoneAPI(mic)
    assert api.height == 0
    api.set_height(10)
    assert api.height == 10


def test_set_height_negative():
    mic = UDPSocket(None)
    api = MicrophoneAPI(mic)
    with pytest.raises(AssertionError):
        api.set_height(-1)


def test_set_height_float():
    mic = UDPSocket(None)
    api = MicrophoneAPI(mic)
    api.set_height(2.5)
    assert api.height == 2.5


def test_elevation():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"elevation":90}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert api.get_elevation() == np.deg2rad(90)
    assert api.elevation == np.deg2rad(90)

def test_azimuth():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"azimuth":46}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert api.get_azimuth() == np.deg2rad(46)
    assert api.azimuth == np.deg2rad(46)


def test_azimuth_recv_error():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"osc":{"error":[400,{"desc":"message not understood"}]}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    api.azimuth = 0.5
    assert api.get_azimuth() == 0.5


def test_azimuth_sendto_error():
    """ Invalid address given
    """
    api = MicrophoneAPI(UDPSocket(None))
    with pytest.raises(Exception):
        api.get_azimuth()

def test_direction_basic():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":0}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert np.allclose(api.get_direction(), [0.0, 0.0, 1.0])
    assert api.azimuth == np.deg2rad(0)
    assert api.elevation == np.deg2rad(0)


def test_direction_vertical():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":90}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert np.allclose(api.get_direction(), [0.0, 1.0, 0.0])
    assert api.azimuth == np.deg2rad(0)
    assert api.elevation == np.deg2rad(90)


def test_speaking():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"in1":{"peak":-5}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert api.is_speaking()
    assert api.speaking


def test_not_speaking():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"in1":{"peak":-70}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert not api.is_speaking()
    assert not api.speaking


@given(st.integers(min_value=0, max_value=359),
       st.integers(min_value=0, max_value=90))
def test_direction_unit(alpha, beta):
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":' + str(alpha) +
               ',"elevation":' + str(beta) + '}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    res = api.get_direction()
    sumofsquares = np.sum(res ** 2)
    assert np.isclose(api.azimuth, np.deg2rad(alpha))
    assert np.isclose(api.elevation, np.deg2rad(beta))
    assert np.isclose(sumofsquares, 1)
    assert res[0] <= 1
    assert res[1] <= 1
    assert res[2] <= 1


@given(st.integers(min_value=0, max_value=90))
def test_elevation_prop(a):
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"elevation":' +
                                        str(a) + '}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert np.isclose(api.get_elevation(), np.deg2rad(a))
    assert np.isclose(api.elevation, np.deg2rad(a))
