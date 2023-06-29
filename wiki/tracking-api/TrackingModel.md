## Description
The abstract TrackingModel class is defined in `TrackingModel.py`. It is the
class that has to be extended by every other tracking model (e.g. AudioModel).
The main purpose of the TrackingModel is to enforce the implementation of a
`point`. This is the method that is being called by the
[UpdateThread](./wiki/tracking-api/UpdateThread.md) continuously and furthermore we decided to give each model
a different idle time after `point` has been executed since they have proven to work
better with different waiting times. To achieve that they all implement the abstract `sleep` method.

This allows for easy development of new models that can be integrated into the system.
It is expected that `point` method sends move command to camera, as `UpdateThread` only controls general flow of tracking.

The current implementations of the TrackingModel are:
* [ObjectModel](./wiki/tracking-api/object-model/ObjectModel.md)
    * [WaitObjectAudioModel](./wiki/tracking-api/object-model/WaitObjectAudioModel.md)
    * [QuickChangeObjectAudioModel](./wiki/tracking-api/object-model/QuickChangeObjectAudioModel.md)
* [AudioModel](./wiki/tracking-api/AudioModel.md)
* [PresetModel](./wiki/tracking-api/PresetModel.md)

In order to create a tracking model, a new ModelCode has to be added as
described in `integration` into ModelCode enum. Moreover, the `start_thread_endpoint` has to be
modified as described [here](./wiki/web-ui/Tracking-endpoints.md).
