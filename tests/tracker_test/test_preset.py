import os
import pytest
import numpy as np
from avonic_speaker_tracker.preset_model.preset import Preset, PresetCollection


@pytest.fixture()
def preset_collection():
    col = PresetCollection(filename=None)
    return col

@pytest.fixture()
def preset_collection_with_file():
    col = PresetCollection(filename="test.json")
    yield col
    os.remove("test.json")


def test_edit_preset(preset_collection: PresetCollection):
    name : str = "preset"
    camera_angle: np.ndarray = np.array([1, 2, 5000])
    microphone_direction: np.ndarray = np.array([1, 2, 3])
    preset_collection.add_preset(name, camera_angle, microphone_direction)

    current_preset: Preset = preset_collection.preset_locations["preset"]
    assert np.array_equal(current_preset.microphone_direction, microphone_direction) \
        and np.array_equal(current_preset.camera_info, camera_angle)

    new_camera_angle:np.ndarray = np.array([2, 3, 0])
    new_microphone_direction:np.ndarray = np.array([1, 3, 5])

    preset_collection.edit_preset(name, new_camera_angle, new_microphone_direction)

    new_preset: Preset = preset_collection.preset_locations["preset"]
    assert np.array_equal(new_preset.microphone_direction, new_microphone_direction) \
        and np.array_equal(new_preset.camera_info, new_camera_angle)


def test_name_already_contained(preset_collection: PresetCollection):
    preset_collection.add_preset("preset", np.array([1, 2, 5000]), np.array([1, 2, 3]))
    with pytest.raises (AssertionError):
        preset_collection.add_preset("preset", np.array([1, 2, 5000]), np.array([1, 2, 3]))


def test_remove_preset(preset_collection: PresetCollection):
    preset_collection.add_preset("preset", np.array([1, 2, 5000]), np.array([1, 2, 3]))
    preset_collection.remove_preset("preset")
    assert "preset" not in preset_collection.preset_locations


def test_get_preset_lists(preset_collection: PresetCollection):
    preset_collection.add_preset("preset", np.array([1, 2, 5000]), np.array([1, 2, 3]))
    preset_collection.add_preset("preset2", np.array([1, 2, 5000]), np.array([1, 2, 3]))
    preset_collection.add_preset("preset3", np.array([1, 2, 5000]), np.array([1, 2, 3]))
    preset_collection.add_preset("preset4", np.array([1, 2, 5000]), np.array([1, 2, 3]))

    assert preset_collection.get_preset_list() == ["preset", "preset2", "preset3", "preset4"]


def test_get_preset_info(preset_collection: PresetCollection):
    preset_collection.add_preset("preset", np.array([1, 2, 5000]), np.array([1, 2, 3]))
    preset_collection.add_preset("preset2", np.array([2, 3, 0]), np.array([4, 5, 6]))
    preset_collection.add_preset("preset3", np.array([3, 4, 16000]), np.array([7, 8, 9]))
    preset_collection.add_preset("preset4", np.array([4, 5, 0]), np.array([10, 11, 12]))

    info = preset_collection.get_preset_info("preset3")
    assert np.array_equal(info[0], np.array([3, 4, 16000])) and np.array_equal(
        info[1], np.array([7, 8, 9]))


def test_presets_with_file_system(preset_collection_with_file: PresetCollection):
    preset_collection_with_file = PresetCollection(filename="test.json")
    preset_collection_with_file.add_preset("preset-to-add", np.array([0, 0, 0]), np.array([0, 0]))
    assert "preset-to-add" in preset_collection_with_file.preset_locations
    new_preset_collection = PresetCollection(filename="test.json")
    assert "preset-to-add" in new_preset_collection.preset_locations
