import pytest
import numpy as np
from unittest import mock
from avonic_speaker_tracker.object_model.model_one.STModelOne import HybridTracker
from avonic_camera_api.camera_adapter import ResponseCode

@pytest.fixture()
def obj_tracker():
    cam_mock = mock.Mock()
    mic_mock = mock.Mock()
    nn_mock = mock.Mock()
    stream_mock = mock.Mock()

    obj_tracker = HybridTracker(cam_mock, mic_mock, nn_mock, stream_mock, "")

    return obj_tracker

def generate_test_find_box():
    return [
        # test 1
        ([np.array( [0, 0, 10, 15]),
          np.array([100, 250, 300, 500]),
          np.array([1300, 200, 1500, 250]),
          np.array([1900, 300, 1920, 1500])
         ], np.array([1330, 225]), np.array([1300, 200, 1500, 250])),
        # test 2
        ([np.array( [0, 0, 10, 15]),
          np.array([100, 250, 300, 500]),
          np.array([1300, 200, 1500, 250]),
          np.array([1900, 300, 1920, 1500])
         ], np.array([1700, 900]), np.array([1900, 300, 1920, 1500])),
        # test 3
        ([np.array( [0, 0, 10, 15]),
          np.array([100, 250, 300, 500]),
          np.array([1300, 200, 1500, 250]),
          np.array([1900, 300, 1920, 1500])
         ], np.array([120, 200]), np.array([100, 250, 300, 500]))
    ]

@pytest.mark.parametrize("all_boxes, pixel, expected", generate_test_find_box())
def test_find_box(obj_tracker: HybridTracker, all_boxes, pixel, expected):

    assert (expected == obj_tracker.find_box(all_boxes, pixel)).all()

def generate_test_find_next_box():
    return [
        # test 1
        (np.array([1350, 250, 1600, 260]),
         [np.array( [0, 0, 10, 15]),
          np.array([100, 250, 300, 500]),
          np.array([1300, 200, 1500, 250]),
          np.array([1900, 300, 1920, 1500])
         ], np.array([1300, 200, 1500, 250])),
        # test 2
        (np.array([1700, 350, 1800,900]),
         [np.array( [0, 0, 10, 15]),
          np.array([100, 250, 300, 500]),
          np.array([1300, 200, 1500, 250]),
          np.array([1900, 300, 1920, 1500])
         ], np.array([1900, 300, 1920, 1500])),
        # test 3
        (np.array([120, 100, 150, 300]), 
         [np.array( [0, 0, 10, 15]),
          np.array([100, 250, 300, 500]),
          np.array([1300, 200, 1500, 250]),
          np.array([1900, 300, 1920, 1500])
         ], np.array([100, 250, 300, 500]))
    ]

@pytest.mark.parametrize("all_boxes, prev_box, expected", generate_test_find_next_box())
def test_find_next_box(obj_tracker: HybridTracker, all_boxes, prev_box, expected):

    assert (expected == obj_tracker.find_next_box(all_boxes, prev_box)).all()

def test_no_boxes(obj_tracker: HybridTracker):
    assert obj_tracker.find_next_box(np.array([1, 1, 1, 1]), []) is None

def test_current_box_is_none(obj_tracker: HybridTracker):
    assert obj_tracker.find_next_box(None, [np.array([1, 1, 1, 1])]) is None

def test_no_speaker_talking(obj_tracker: HybridTracker):
    obj_tracker.mic_api.is_speaking.return_value = False
#    obj_tracker.safely_get_frame.return_value = None
    def mocked_get_frame(x):
        return None
    
    def mocked_get_movement(x, y):
        return (np.array([1, 2]), np.array([1, 2]))

    with mock.patch("avonic_speaker_tracker.object_model.model_one.STModelOne.HybridTracker.safely_get_frame", mocked_get_frame):
        with mock.patch("avonic_speaker_tracker.object_model.model_one.STModelOne.HybridTracker.get_movement_to_box", mocked_get_movement):
            obj_tracker.last_tracked = np.array([120, 100, 150, 300])

            obj_tracker.nn.get_bounding_boxes.return_value = [np.array( [0, 0, 10, 15]),
                  np.array([100, 250, 300, 500]),
                  np.array([1300, 200, 1500, 250]),
                  np.array([1900, 300, 1920, 1500])
                 ]

            def mocked_move(x1, x2, x3, x4):
                pass


            obj_tracker.cam_api.move_relative.side_effect = mocked_move
            obj_tracker.point()

def test_no_speaker_talking_no_last_tracked(obj_tracker: HybridTracker):
    obj_tracker.mic_api.is_speaking.return_value = False

    def mocked_get_frame(x):
        return None
    
    with mock.patch("avonic_speaker_tracker.object_model.model_one.STModelOne.HybridTracker.safely_get_frame", mocked_get_frame):

        obj_tracker.nn.get_bounding_boxes.return_value = []

        def mocked_move(x1, x2, x3, x4):
            assert False


        obj_tracker.cam_api.move_relative.side_effect = mocked_move
        obj_tracker.point()

def test_no_speaker_talking_no_new_box(obj_tracker: HybridTracker):
    obj_tracker.mic_api.is_speaking.return_value = False
    
    def mocked_get_frame(x):
        return None
    with mock.patch("avonic_speaker_tracker.object_model.model_one.STModelOne.HybridTracker.safely_get_frame", mocked_get_frame):

        obj_tracker.last_tracked = np.array([120, 100, 150, 300])

        obj_tracker.nn.get_bounding_boxes.return_value = []

        def mocked_move(x1, x2, x3, x4):
            assert False


        obj_tracker.cam_api.move_relative.side_effect = mocked_move
        obj_tracker.point()

def test_bad_mic():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    nn_mock = mock.Mock()
    stream_mock = mock.Mock()

    mic_api.is_speaking.return_value = True 

    mic_api.get_direction.return_value = "string"

    obj_tracker = HybridTracker(cam_api, mic_api, nn_mock, stream_mock, "")

    obj_tracker.point()

    assert cam_api.get_direction.call_count == 0

def test_bad_cam():
    cam_api = mock.Mock()
    mic_api = mock.Mock()
    nn_mock = mock.Mock()
    stream_mock = mock.Mock()

    mic_api.is_speaking.return_value = True 
    mic_api.get_direction.return_value = np.array([1, 2, 3])
    cam_api.get_direction.return_value = ResponseCode.CANCELED

    obj_tracker = HybridTracker(cam_api, mic_api, nn_mock, stream_mock, "")

    obj_tracker.point()

    assert cam_api.move_relative.call_count == 0
    assert cam_api.move_absolute.call_count == 0