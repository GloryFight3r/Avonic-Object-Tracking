## Description

Audio Model - is the key model of the project and is part of the Tracking module.

## Calibration
Prior to use, `AudioModel` needs to be calibrated. `AudioModel` contains a `Calibration` object which contains spacial information about the room
represented in speakers position in it with relation to microphone and camera. 

As `AudioModel` relies on speaker's plane height, `Calibration` is structured in a way that allows changing speaker plane's height without need to recalibrate the system, assuming camera and microphone are not moved. 

`Calibration` stores vector of direction from camera to microphone, microphone height and calibrated points with a speaker.

Each entry of `speaker_points` contains 2 vectors - from microphone and camera towards a speaker. Methods in calibration are made in the way, that they support unlimited
number of speaker points, but WebUI limits number the user to only 3. It is possible to load more using a file, but it will be impossible to edit via the WebUI.
In addition to that, `Calibration` stores most recent version of all the data within the object, so it is not lost after restart of the app, or can be imported from a different system.

## Calibration process

## Algorithm of the model

When vector from camera to the microphone of the real length is obtained, the actual tracking can start.
At each call of the point method, vector from the microphone to the speaker is prolonged to find intersection with the plane.
As then you have a point of the speaker, the only thing left to obtain vector from camera to speaker is to add 2 previously calculated vectors - from microphone to the speaker and from to the microphone. When vectors are added, the move command to camera is sent, that converts direction of the vector to angles and actually moves camera.

## Modifications

As we have noticed that video might appear quite jittery, we have decided to implement adaptive speed. It simply proportionally changes speed parameter of the movement, so camera is moved at slower speeds when camera needs to be moved only a few degrees, and faster when bigger rotations are involved.

We have also decided to improve the model by adding adaptive zooming. The model would zoom in if a speaker is far from camera and zoom out if speaker is far frm the camera. However, as it may be not applicable in some scenarios, we have decided to separate it into a different model, so users can choose between a normal and adaptive zooming strategies.

## Main components
- `AudioModelNoAdaptiveZoom.py` - contains main method that combines all of the helper methods, to actually point the camera based on calibration.
- `AudioModel.py` - contains main method that combines all of the helper methods, to actually point the camera based on calibration.
- `calibration.py` - contains definition of `Calibration` class, that represents interface to interact when calibrating the system, and methods to finalize calibration and store the contained data.
- `utils/coordinate_translation.py` - contains method that performs calculations described in the algorithm of the model section.