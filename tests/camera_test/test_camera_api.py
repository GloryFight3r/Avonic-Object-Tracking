import numpy as np
from unittest import mock
import pytest
from maat_camera_api.converter import angle_vector, vector_angle
from maat_camera_api.camera_control_api import CameraAPI, CompressedFormat, ImageSize


def test_angle_vector_basic():
    alpha = 0
    beta = 0
    assert np.array_equal(angle_vector(alpha, beta), [0.0, 0.0, 1.0])


def test_angle_vector_complex():
    alpha = -30
    beta = 60
    # x is +0.25 because the pan angle goes clockwise,
    # therefore this negative one goes counterclockwise,
    # so towards the x-axis
    # This is the correct value, do not edit!!
    result = np.array([0.25, np.sqrt(3) / 2, np.sqrt(3) / 4])
    assert np.allclose(angle_vector(np.deg2rad(alpha), np.deg2rad(beta)), result)


def test_vector_angle_bad_weather():
    # 4 floats
    result = np.array([0.25, np.sqrt(3) / 2, np.sqrt(3) / 4, 0.3])
    with pytest.raises(TypeError) as excinfo:
        vector_angle(result)
    assert "Vector must contain three floats and be instance of np.ndarray" == str(excinfo.value)
    result_int = np.array([1.0, 1.0])
    with pytest.raises(TypeError) as excinfo:
        vector_angle(result_int)
    assert "Vector must contain three floats and be instance of np.ndarray" == str(excinfo.value)


def test_vector_angle_basic():
    assert vector_angle(np.array([0.0, 0.0, 1.0])) == (0, 0)


def test_vector_angle_complex_normalised():
    alpha = -30
    beta = 60
    (a, b) = vector_angle(np.array([0.25, np.sqrt(3)/2, np.sqrt(3)/4]))
    assert pytest.approx(a) == np.deg2rad(alpha)
    assert pytest.approx(b) == np.deg2rad(beta)


def test_vector_angle_complex():
    """ not normalized, length of vector is 2 """
    alpha = -30
    beta = 60
    (a, b) = vector_angle(np.array([0.5, np.sqrt(3), np.sqrt(3)/2]))
    assert pytest.approx(a) == np.deg2rad(alpha)
    assert pytest.approx(b) == np.deg2rad(beta)


def test_vector_angle_invalid():
    with pytest.raises(ValueError) as excinfo:
        vector_angle(np.array([0.0, 0.0, 0.0]))
    assert "Vector not normalizable" == str(excinfo.value)


def test_vector_angle_invalid_type():
    with pytest.raises(TypeError) as excinfo:
        vector_angle([1, 2])
    assert "Vector must contain three floats and be instance of np.ndarray" == str(excinfo.value)


@pytest.fixture()
def cam_api():
    mock_cam = mock.Mock()
    cam_api = CameraAPI(None, mock_cam)

    return cam_api


def generate_codec_tests():
    return [
        (CompressedFormat.MJPEG, 
            '{"SetEnv":{"VideoEncode":[{"stMaster": {"emVideoCodec":1},"nChannel":0}]}}'),
        (CompressedFormat.H264, 
            '{"SetEnv":{"VideoEncode":[{"stMaster": {"emVideoCodec":5},"nChannel":0}]}}'),
        (CompressedFormat.H265, 
            '{"SetEnv":{"VideoEncode":[{"stMaster": {"emVideoCodec":7},"nChannel":0}]}}')
    ]


@pytest.mark.parametrize("format, expected", generate_codec_tests())
def test_camera_codec(cam_api, format, expected, monkeypatch):
    def mocked_method(command):
        assert command == expected

    monkeypatch.setattr(cam_api.camera_http, "send", mocked_method)
    cam_api.set_camera_codec(format)


def generate_format_tests():
    return [
        (ImageSize.P1280_720,
            '{"SetEnv":{"VideoEncode":[{"stMaster": {"emImageSize":4},"nChannel":0}]}}'),
        (ImageSize.P1920_1080,
            '{"SetEnv":{"VideoEncode":[{"stMaster": {"emImageSize":5},"nChannel":0}]}}'),
    ]


@pytest.mark.parametrize("format, expected", generate_format_tests())
def test_image_size(cam_api, format, expected, monkeypatch):
    def mocked_method(command):
        assert command == expected

    monkeypatch.setattr(cam_api.camera_http, "send", mocked_method)
    cam_api.set_image_size(format)


def generate_frame_rate_tests():
    return [
        (25, '{"SetEnv":{"VideoEncode":[{"stMaster": {"nFrameRate":25},"nChannel":0}]}}'),
        (50, '{"SetEnv":{"VideoEncode":[{"stMaster": {"nFrameRate":50},"nChannel":0}]}}'),
    ]


@pytest.mark.parametrize("frame, expected", generate_frame_rate_tests())
def test_frame_rate(cam_api, frame, expected, monkeypatch):
    def mocked_method(command):
        assert command == expected

    monkeypatch.setattr(cam_api.camera_http, "send", mocked_method)
    cam_api.set_frame_rate(frame)


def generate_frame_rate_bad_tests():
    return [
        0,
        -1,
        61
    ]


@pytest.mark.parametrize("frame_rate", generate_frame_rate_bad_tests())
def test_frame_bad_rate(cam_api, frame_rate):
    with pytest.raises(AssertionError):
        cam_api.set_frame_rate(frame_rate)


def generate_frame_rate_l_tests():
    return [
        (25, '{"SetEnv":{"VideoEncode":[{"stMaster": {"nIFrameInterval":25},"nChannel":0}]}}'),
        (50, '{"SetEnv":{"VideoEncode":[{"stMaster": {"nIFrameInterval":50},"nChannel":0}]}}'),
    ]


@pytest.mark.parametrize("frame_rate_l, expected", generate_frame_rate_l_tests())
def test_frame_rate_interval(cam_api, frame_rate_l, expected, monkeypatch):
    def mocked_method(command):
        assert command == expected

    monkeypatch.setattr(cam_api.camera_http, "send", mocked_method)
    cam_api.set_i_frame_rate(frame_rate_l)


def generate_frame_rate_bad_l_tests():
    return [
        0,
        -1,
        301
    ]


@pytest.mark.parametrize("frame_rate_l", generate_frame_rate_bad_l_tests())
def test_frame_rate_bad_interval(cam_api, frame_rate_l):
    with pytest.raises(AssertionError):
        cam_api.set_i_frame_rate(frame_rate_l)
