## Description
This module is responsible for the actual tracking code itself. Using the provided APIs, it can control the camera based on collected and provided data. It contains:
* `updater.py` - unified UpdateThread class that describes the behavior of the "tracking thread" that is launched when the user turns on the tracking.
* `utils` - utilities that can be used by multiple models or other developers for developing their own models.

## Use cases
As the tracking module contains the necessary software for the actual following, it is used in WebUI to provide access to the following functionality to users.
The module is developed with future engineers in mind, so it is easy for developers to add their own models to the system.
## Related pages
* [UpdateThread](./wiki/tracking-api/UpdateThread.md) - to learn about how models are run.
* [TrackingModel](./wiki/tracking-api/TrackingModel.md) - to learn about our Model system and implemented models.
* [PresetModel](./wiki/tracking-api/PresetModel.md) - to learn about the preset tracking model.
* [AudioModel](./wiki/tracking-api/AudioModel.md) - to learn about the audio tracking model.
* [ObjectModel](./wiki/tracking-api/object-model/object-model-overview.md) - to learn about the object tracking models.
* [Calibration](./wiki/tracking-api/Calibration.md) - to learn about the Calibration class.
