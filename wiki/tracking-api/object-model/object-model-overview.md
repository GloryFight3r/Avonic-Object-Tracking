## Description
The ObjectModel is the model that takes care of object tracking. It requires no
actions from the user to set up. This model is in the ObjectModel.py file.

It is only used in combination with the AudioModel, since one of the
requirements of the project was to use the microphone to track speakers.
However, this model can be extended to use only object tracking. In order to
properly extend this model, only the `point()` method has to be implemented.
We have implemented two different ways for object tracking.

## Main components
- [`ObjectModel.py`](./wiki/tracking-api/object-model/ObjectModel.md)
- [`QuickChangeObjectAudioModel.py`](./wiki/tracking-api/object-model/QuickChangeObjectAudioModel.md)
- [`WaitObjectAudioModel.py`](./wiki/tracking-api/object-model/WaitObjectAudioModel.md)
- [`yolov8.py`](./wiki/tracking-api/object-model/yolov8.md)
