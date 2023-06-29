## Description
Camera API module contains all of the functionality related to the Camera. It contains:
* CameraAPI - class that communicates with Camera via VISCA protocol
* CameraSocket - initializes a interface for communication with camera, implementing an adapter pattern together with CameraAPI
* `converter.py` - contains functions for converting between angles and vectors

## Use cases
CameraAPI module is used in the `web_app` as a high level interface for interactions with a camera. It is also used in SpeakerTracker module as it controls camera movement when following the speaker.

## Related pages
* [CameraSocket](./wiki/camera-api/CameraSocket.md)
* [CameraHTTP](./wiki/camera-api/CameraHTTP.md)
* [CameraAPI class](./wiki/camera-api/CameraAPI.md)
* [converter.py](./wiki/camera-api/converter.py.md)
* [FootageThread](./wiki/camera-api/FootageThread.md)