from microphone_api.microphone_control_api import *
import numpy as np
import pytest
from unittest import mock


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
    sock.recvfrom.return_value = (bytes('{"osc":{"error":[400,{"desc":"message not understood"}]}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    with pytest.raises(Exception):
        api.get_azimuth()


def test_azimuth_sendto_error():
    """ Invalid address given
    """
    api = MicrophoneAPI(UDPSocket(None))
    with pytest.raises(Exception):
        api.get_azimuth()


def test_elevation():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"elevation":90}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert api.get_elevation() == np.deg2rad(90)
    assert api.elevation == np.deg2rad(90)

def test_direction_basic():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"azimuth":0,"elevation":0}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert np.allclose(api.get_direction(), [0.0, 0.0, 1.0])
    assert api.azimuth == np.deg2rad(0)
    assert api.elevation == np.deg2rad(0)

def test_direction_vertical():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"azimuth":0,"elevation":90}}}\r\n', "ascii"), None)
    api = MicrophoneAPI(UDPSocket(None, sock))
    assert np.allclose(api.get_direction(), [0.0, -1.0, 0.0])
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
