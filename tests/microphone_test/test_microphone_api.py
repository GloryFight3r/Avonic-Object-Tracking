import json
from unittest import mock
from hypothesis import given, strategies as st
import numpy as np
from microphone_api.microphone_adapter import MicrophoneSocket
from microphone_api.microphone_control_api import MicrophoneAPI



def test_init():
    sock = MicrophoneSocket(None)
    mic = MicrophoneAPI(sock)

    assert mic.elevation == 0.0
    assert mic.azimuth == 0.0
    assert mic.speaking is False
    assert mic.threshold == -55

def test_elevation():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"elevation":90}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert api.get_elevation() == np.deg2rad(90)
    assert api.elevation == np.deg2rad(90)


def test_azimuth():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"beam":{"azimuth":46}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert api.get_azimuth() == np.deg2rad(46)
    assert api.azimuth == np.deg2rad(46)


def test_elevation_recv_error():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"osc":{"error":[400,{"desc":"message not understood"}]}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    api.elevation = 0.5
    assert api.get_elevation() == 0.5


def test_azimuth_recv_error():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"osc":{"error":[400,{"desc":"message not understood"}]}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    api.azimuth = 0.5
    assert api.get_azimuth() == 0.5


def test_direction_recv_error():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"osc":{"error":[400,{"desc":"message not understood"}]}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert json.loads(api.get_direction())[0] == 400


def test_speaking_recv_error():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"osc":{"error":[400,{"desc":"message not understood"}]}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert json.loads(api.is_speaking())[0] == 400


def test_direction_recv_invalid_json():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"not":"a microphone"}', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert api.get_direction() == "Unable to get direction from microphone, response was: {\"not\":\"a microphone\"}"


def test_speaking_recv_invalid_json():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"i am a":"rocket launcher"}', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert api.is_speaking() == "Unable to get peak loudness, response was: {\"i am a\":\"rocket launcher\"}"


def test_direction_recv_gibberish():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('asdf', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert api.get_direction() == "Did not receive a valid JSON," \
                                  " are you sure you are communicating with the microphone? Received: asdf"


def test_speaking_recv_gibberish():
    """ Invalid command
    """
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('gugu gaga', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert api.is_speaking() == "Did not receive a valid JSON," \
                                " are you sure you are communicating with the microphone? Received: gugu gaga"


def test_elevation_sendto_error():
    """ Invalid address given
    """
    api = MicrophoneAPI(MicrophoneSocket())
    api.elevation = 0.5
    assert api.get_elevation() == 0.5


def test_azimuth_sendto_error():
    """ Invalid address given
    """
    api = MicrophoneAPI(MicrophoneSocket())
    api.azimuth = 0.5
    assert api.get_azimuth() == 0.5


def test_direction_sendto_error():
    """ Invalid address given
    """
    api = MicrophoneAPI(MicrophoneSocket())
    api.elevation = np.pi/2
    api.azimuth = 0
    assert api.get_direction() == "Microphone returned nothing."


def test_speaking_sendto_error():
    """ Invalid address given
    """
    api = MicrophoneAPI(MicrophoneSocket())
    api.speaking = True
    assert api.is_speaking() == "Microphone returned nothing."


def test_direction_basic():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":0}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)

    assert np.allclose(api.get_direction(), [0.0, 0.0, 1.0])
    assert api.azimuth == np.deg2rad(0)
    assert api.elevation == np.deg2rad(0)


def test_direction_vertical(monkeypatch):
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":90}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    monkeypatch.setattr(api, "is_speaking", lambda: True)
    # this is the correct value for a microphone pointing downwards, do not edit!!
    assert np.allclose(api.get_direction(), [0.0, -1.0, 0.0])
    assert api.azimuth == np.deg2rad(0)
    assert api.elevation == np.deg2rad(90)


def test_speaking():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"in1":{"peak":-5}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert api.is_speaking()
    assert api.speaking


def test_reverse_order_speaking(monkeypatch):
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value =\
        (bytes('{"m":{"beam":{"azimuth":0,"elevation":90}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    monkeypatch.setattr(api, "is_speaking", lambda: True)
    assert np.allclose(api.get_direction(), [0.0, -1.0, 0.0])


def test_reverse_order_direction():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"in1":{"peak":-5}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert np.allclose(api.get_direction(), [0.0, 0.0, 1.0])
    assert api.speaking is True


def test_not_speaking():
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = (bytes('{"m":{"in1":{"peak":-70}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert not api.is_speaking()
    assert not api.speaking


@given(st.integers(min_value=0, max_value=359),
       st.integers(min_value=0, max_value=90))
def test_direction_unit(alpha, beta):
    sock = mock.Mock()
    sock.sendto.return_value = 48
    sock.recvfrom.return_value = \
        (bytes('{"m":{"beam":{"azimuth":' + str(alpha) +
               ',"elevation":' + str(beta) + '}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
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
                                        str(a) + '}}}\r\n', "ascii"), ("0.0.0.1", 45))
    mic_sock = MicrophoneSocket(sock=sock)
    mic_sock.address = ("0.0.0.1", 45)
    api = MicrophoneAPI(mic_sock)
    assert np.isclose(api.get_elevation(), np.deg2rad(a))
    assert np.isclose(api.elevation, np.deg2rad(a))


def test_connect():
    sock = mock.Mock()
    api = MicrophoneAPI(MicrophoneSocket(sock=sock))
    expected = ('0.0.0.0', 45)
    api.set_address(expected)
    assert api.sock.address == expected


def test_connect_invalid():
    sock = mock.Mock()
    expected = ('0.0.0.0', 45)
    api = MicrophoneAPI(MicrophoneSocket(sock=sock, address=expected))
    api.set_address(None)
    assert api.sock.address == expected
