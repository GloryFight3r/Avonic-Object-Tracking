## Description
The calibration class contains all the necessary vectors for calculating the
position of the camera and the speaker. These directions are added during the
calibration process and written to a file using the `record` method. To load the
vectors again after a server restart, the `load` method is used to load the
calibration from the file.
By default, this file is called "calibration.json".

The precise calculations used to determine the position of the camera and the
speaker are described in
[Calibration and Translation](./wiki/general/Calibration-and-Translation.md).
