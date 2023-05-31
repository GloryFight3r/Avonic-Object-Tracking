import pytest
import numpy as np
import avonic_speaker_tracker.coordinate_translation

def generate_good_pairs_of_combinations():
    # Check values at:
    # https://www.geogebra.org/calculator/wwejbfhe
    # Format:
    #   camera-to-microphone vector
    #   microphone-to-speaker vector
    #   height from the speaker plane to microphone
    #   expected vector of correct distance camera-to-speaker
    return [
        (np.array([1.8, 1.8, 6]), np.array([1.9, -1.2, 2.7]),
        1.2, np.array([3.7, 0.6, 8.7])),
    ]

def generate_bad_pairs_of_combinations():
    return [
        (np.array([-1.9, 1.3, -1.5, 1]), np.array([-1.4, -1.7, -0.1]),
        1.7),
        (np.array([-1.9, 1.3, -1.5, 1]), np.array([-1.4, -1.7, -0.1]),
        1.7),
        (np.array([[-1.9, 1.3, -1.5, 1], [1.0, -2.0, 3.0, 4.0]]), np.array([-1.4, -1.7, -0.1]),
        1.7),
        (np.array([-1.9, 1.3]), np.array([-1.4, -1.7, -0.1]),
        1.7),
        (np.array([[-1.9], [1.3], [1.7]]), np.array([-1.4, -1.7, -0.1]),
        1.7),
        (np.array([-1.4, -1.7, -0.1]), np.array([[-1.9], [1.3], [1.7]]),
        1.7),
        (np.array([[-1.9, 1.3, -1.5], [1, 2, 4]]), np.array([-1.4, -1.7, -0.1, 2]),
        1.7),
        (np.array([[-1.5, 3, 0.3]]), np.array([2.8, -2.1, 5.2]),
        2.1),
        (np.array([-1.5, 3, 0.3]), np.array([[2.8, -2.1, 5.2]]),
        2.1),
        (np.array([-1.9, 1.3, -1.5]), np.array([[-1.4, -1.7, -0.1], [1, 1, 1]]),
        1.7),
        (np.array([-1.9, 1.3, -1.5]), np.array([[-1.4, -1.7, -0.1, 1], [2, 2, 2, 3]]),
        1.7),
    ]

@pytest.mark.parametrize("camera_to_microphone, from_microphone_to_speaker,\
     from_speaker_ceiling_distance, expected", generate_good_pairs_of_combinations())
def test_translate_good_weather(camera_to_microphone,
    from_microphone_to_speaker, from_speaker_ceiling_distance, expected):
    assert np.allclose(
        avonic_speaker_tracker.coordinate_translation.translate_microphone_to_camera_vector(
            camera_to_microphone, from_microphone_to_speaker, from_speaker_ceiling_distance)
            , expected)

@pytest.mark.parametrize("camera_to_microphone, from_microphone_to_speaker,\
     from_speaker_ceiling_distance", generate_bad_pairs_of_combinations())
def test_translate_bad_weather(camera_to_microphone,
    from_microphone_to_speaker, from_speaker_ceiling_distance):
    with pytest.raises (TypeError) as excinfo:
        avonic_speaker_tracker.coordinate_translation.translate_microphone_to_camera_vector(
            camera_to_microphone, from_microphone_to_speaker, from_speaker_ceiling_distance)
    assert "Not a 3D vector" == str(excinfo.value)
