import os
from unittest import mock
import json
import pytest
import numpy as np
from maat_tracking.preset_model.preset import Preset, PresetCollection


@pytest.fixture()
def preset_collection():
    col = PresetCollection(filename="")
    return col


@pytest.fixture()
def preset_collection_with_file():
    col = PresetCollection(filename="test.json")
    yield col
    os.remove("test.json")


def test_edit_preset(preset_collection: PresetCollection):
    name: str = "preset"
    camera_angle: np.ndarray = np.array([1, 2, 5000])
    microphone_direction: np.ndarray = np.array([1, 2, 3])
    preset_collection.add_preset(name, camera_angle, microphone_direction)

    current_preset: Preset = preset_collection.preset_locations["preset"]
    assert np.array_equal(current_preset.microphone_direction, microphone_direction) \
           and np.array_equal(current_preset.camera_info, camera_angle)

    new_camera_angle: np.ndarray = np.array([2, 3, 0])
    new_microphone_direction: np.ndarray = np.array([1, 3, 5])

    preset_collection.edit_preset(name, new_camera_angle, new_microphone_direction)

    new_preset: Preset = preset_collection.preset_locations["preset"]
    assert np.array_equal(new_preset.microphone_direction, new_microphone_direction) \
           and np.array_equal(new_preset.camera_info, new_camera_angle)


def test_name_already_contained(preset_collection: PresetCollection):
    preset_collection.add_preset("preset", np.array([1, 2, 5000]), np.array([1, 2, 3]))
    with pytest.raises(AssertionError):
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
    preset_collection_with_file.add_preset("preset-to-add",
                                           np.array([0, 0, 0]), np.array([0, 0, 0]))
    assert "preset-to-add" in preset_collection_with_file.preset_locations
    new_preset_collection = PresetCollection(filename="test.json")
    assert "preset-to-add" in new_preset_collection.preset_locations


def test_with_file_corrupted_missed_one_mic_vector():
    try:
        data = {
            "1": {
                "camera_info": [
                    1.57055,
                    0.52341,
                    243.423
                ],
                "microphone_direction": [
                    -0.65177,
                    -0.62932
                ]
            },
            "3": {
                "camera_info": [
                    -0.78528,
                    0.7845,
                    1000.0
                ],
                "microphone_direction": [
                    -0.65177,
                    -0.62932,
                    -0.42326
                ]
            },
            "2": {
                "camera_info": [
                    0.0,
                    0.0,
                    0.0
                ],
                "microphone_direction": [
                    0.58553,
                    -0.78801,
                    -0.19025
                ]
            }
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_missed_one_mic_vector.json", 'w') as outfile:
            outfile.write(json_string)

        pc = PresetCollection("test_with_file_corrupted_missed_one_mic_vector.json")
        assert np.allclose(pc.preset_locations["1"].microphone_direction,
                           PresetCollection.default_mic_info)
        assert np.allclose(pc.preset_locations["1"].camera_info,
                           np.array([
                               1.57055,
                               0.52341,
                               243.423
                           ]))
    finally:
        os.remove("test_with_file_corrupted_missed_one_mic_vector.json")


def test_with_file_corrupted_missed_one_cam_vector():
    try:
        data = {
            "1": {
                "camera_info": [
                    1.57055,
                    0.52341
                ],
                "microphone_direction": [
                    -0.65177,
                    -0.62932,
                    -0.42326
                ]
            },
            "3": {
                "camera_info": [
                    -0.78528,
                    0.7845,
                    1000.0
                ],
                "microphone_direction": [
                    -0.65177,
                    -0.62932,
                    -0.42326
                ]
            },
            "2": {
                "camera_info": [
                    0.0,
                    0.0,
                    0.0
                ],
                "microphone_direction": [
                    0.58553,
                    -0.78801,
                    -0.19025
                ]
            }
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_missed_one_cam_vector.json", 'w') as outfile:
            outfile.write(json_string)

        pc = PresetCollection("test_with_file_corrupted_missed_one_cam_vector.json")
        assert np.allclose(pc.preset_locations["1"].camera_info,
                           PresetCollection.default_camera_info)
        assert np.allclose(pc.preset_locations["1"].microphone_direction,
                           np.array([
                               -0.65177,
                               -0.62932,
                               -0.42326
                           ]))
    finally:
        os.remove("test_with_file_corrupted_missed_one_cam_vector.json")


def test_with_file_corrupted_missed_full_one_cam_vector():
    try:
        data = {
            "1": {
                "microphone_direction": [
                    -0.65177,
                    -0.62932,
                    -0.42326
                ]
            },
            "3": {
                "camera_info": [
                    -0.78528,
                    0.7845,
                    1000.0
                ],
                "microphone_direction": [
                    -0.65177,
                    -0.62932,
                    -0.42326
                ]
            },
            "2": {
                "camera_info": [
                    0.0,
                    0.0,
                    0.0
                ],
                "microphone_direction": [
                    0.58553,
                    -0.78801,
                    -0.19025
                ]
            }
        }
        json_string = json.dumps(data)
        with open("test_with_file_corrupted_missed_one_cam_vector.json", 'w') as outfile:
            outfile.write(json_string)

        pc = PresetCollection("test_with_file_corrupted_missed_one_cam_vector.json")
        assert np.allclose(pc.preset_locations["1"].camera_info,
                           PresetCollection.default_camera_info)
        assert np.allclose(pc.preset_locations["1"].microphone_direction,
                           PresetCollection.default_mic_info)
    finally:
        os.remove("test_with_file_corrupted_missed_one_cam_vector.json")


def test_set_filename(preset_collection: PresetCollection):
    def x(self):
        pass

    with mock.patch("maat_tracking.preset_model.preset.PresetCollection.load", x):
        assert preset_collection.filename == ""
        preset_collection.set_filename("asdf")
        assert preset_collection.filename == "asdf"


def test_str():
    p = Preset(np.array([1, 2, 5000]), np.array([1, 2, 3]))
    assert str(p) == f"Preset([   1    2 5000], [1 2 3])"
