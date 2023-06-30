## Description

Preset model - is the simplest tracking model included in the Tracking module.
In the preset model, prior to using, the user needs to set up "presets". Preset describes 2 vectors - vector from the camera to the speaker with zoom information, and from the microphone to the speaker. When the model is running, it constantly finds the "closest" microphone vector, and sets the camera to the corresponding position. As a measure of the closeness, we use cosine similarity, which represents the cosine of the angle between 2 vectors.

The model is simple and very lightweight, which is beneficial considering the limited amount of computational power, it uses very simple mathematical concepts. However, as the model is simple, it is not flexible enough, to support continuous tracking. Of course, it can be more precise if you add more presets.

## Main components
- `preset_control.py` - contains methods for selecting the closest presets to a given vector. 
- `preset.py` - PresetCollection stores all of the available presets and provides an interface for removing or editing already existing presets, or adding new presets.
- `PresetModel.py` - contains main method that combines all of the helper methods, to actually point the camera based on created presets.