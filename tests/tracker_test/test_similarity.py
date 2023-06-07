import pytest
import numpy as np
import avonic_speaker_tracker.preset_model.preset_control

def generate_good_pairs_of_vectors():
    return [
        (np.array([1, 0, 0]), np.array([1, 0, 0]), 1),
        (np.array([1, 0, 0]), np.array([0, 1, 0]), 0),
        (np.array([1, 0, 0]), np.array([0, 1, 0]), 0),
        (np.array([1, 0, 0]), np.array([0, 2, 0]), 0),
        (np.array([2, 0, 0]), np.array([2, 0, 0]), 1),
        (np.array([1, 0, 2]), np.array([5, 1, 0]), 0.43852900965),
        (np.array([0, 2, 3]), np.array([0, 2, 7]), 0.95242414719),
    ]

def generate_bad_pairs_of_vectors():
    return [
        (np.array([1, 0, 0, 0]), np.array([1, 0, 0])),
        (np.array([1, 0]), np.array([0, 1, 0, 0])),
        (np.array([1, 0, 2]), np.array([0, 1, 0, 0])),
        (np.array([1, 0, 0]), np.array([0, 1]))
    ]

@pytest.mark.parametrize("a, b, expected", generate_good_pairs_of_vectors())
def test_good_cos_similarity(a, b, expected):
    assert pytest.approx(
        avonic_speaker_tracker.preset_model.preset_control.cos_similarity(a, b)) == expected

@pytest.mark.parametrize("a, b", generate_bad_pairs_of_vectors())
def test_bad_weather_cos_similarity(a, b):
    with pytest.raises (TypeError) as excinfo:
        avonic_speaker_tracker.preset_model.preset_control.cos_similarity(a, b)
    assert "Not a 3D vector" == str(excinfo.value)

def test_cos_similarity_zero_vector():
    a, b = (np.array([1, 0, 0]), np.array([0, 0, 0]))
    with pytest.raises (ValueError) as excinfo:
        avonic_speaker_tracker.preset_model.preset_control.cos_similarity(a, b)
    assert "Impossible to get similarity with zero-vector" == str(excinfo.value)


def generate_good_entries_find_most_similar_preset():
    return [
        (np.array([1, 0, 0]), [np.array([-1, 0, 0]), np.array([1, 0, 0])], 1),
        (np.array([-1, 0, 0]), [np.array([-1, 0, 0]), np.array([1, 0, 0])], 0),
        (np.array([1, 0, 0]), [np.array([1, 0, 0])], 0),
        (np.array([1, 0, 0]), [np.array([0, 2, 0])], 0),
        (np.array([1, 0, 0]), [np.array([-1, 1, 0]), np.array([-1, 0, 0]), np.array([2, 0, 0])], 2),
    ]


@pytest.mark.parametrize("current, presets, expected",
     generate_good_entries_find_most_similar_preset())
def test_good_presets(current, presets, expected):
    assert avonic_speaker_tracker.preset_model.\
        preset_control.find_most_similar_preset(current, presets) == expected


def test_empty_list_most_similar_preset():
    current, presets = (np.array([1, 0, 0]), [])
    with pytest.raises (ValueError) as excinfo:
        avonic_speaker_tracker.preset_model.\
            preset_control.find_most_similar_preset(current, presets)
    assert "Empty list of presets given" == str(excinfo.value)


def test_zero_vector_list_most_similar_preset():
    current, presets = (np.array([0, 0, 0]), [np.array([1, 0, 0])])
    with pytest.raises (ValueError) as excinfo:
        avonic_speaker_tracker.preset_model.\
            preset_control.find_most_similar_preset(current, presets)
    assert "Impossible to get similarity with zero-vector" == str(excinfo.value)
