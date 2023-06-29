# Description
The tracking endpoints are used to select which model to use for tracking and to
start the [tracking thread](./wiki/tracking-api/UpdateThread.md). The tracking endpoint methods
are in the `tracking_endpoints.py` file.


### Add new tracking model
In order to make `start_thread_endpoint` work with a new tracking model, a new
`elif` case has to be added for the new model. In this `elif`, all that is
needed to do is to create a variable called `model` and assign an instance of
your [TrackingModel](./wiki/tracking-api/TrackingModel.md) to it.
In order to allow your model to be chosen for a HTTP request, a new endpoint has
to be created in the `__init__` file with the path `/model_name/track`, which
sets `integration.tracking.value` to the ModelCode corresponding to
your new model.

# API

## Info threads

* __POST__ `/info-thread/start` - Endpoint that starts the thread that updates all the dynamic data. This means the current directions and more for both the camera and microphone.
    - `return`:
        - HTTP 200: successfully started the info thread

* __POST__ `/info-thread/stop` - Endpoint that stops the thread that updates all the dynamic data
    - `return`:
        - HTTP 200: successfully stopped the info thread

* __POST__ `/update/camera` - Endpoint that updates the camera data in the WebUI
    - `return`:
        - HTTP 200: successfully updated the camera coordinates

* __POST__ `/update/microphone` - Endpoint that updates the microphone data in the WebUI
    - `return`:
        - HTTP 200: successfully updated the microphone coordinates

## Tracking thread

* __POST__ `/thread/start` - Endpoint that starts the tracking thread
    - `return`:
        - In case of an error:
            - HTTP 403: the thread has already been started before
        - In case of success:
            - HTTP 200: the thread has successfully been started

* __POST__ `/thread/stop` - Endpoint that stops the tracking thread
    - `return`:
        - HTTP 200: successfully stopped the tracking thread

* __GET__ `/thread/running` - Endpoint that checks whether the tracking thread is running. This means that the thread is not None and that it is alive.
    - `return`:
        - `"is-running"`: a boolean value indicating whether the thread is running or not
## Select tracking type

* __GET__ `/track/preset` - Endpoint that changes the tracking to use the preset model.
    - `return`:
        - `"tracking"`: the enum corresponding to the preset model
        - HTTP 200: the model has successfully been set to the preset model

* __GET__ `/track/calibration` - Endpoint that changes the tracking to use the audio model
    - `return`:
        - `"tracking"`: the enum corresponding to the AudioModel
        - HTTP 200: the model has successfully been set to the AudioModel

* __GET__ `/track/calibration-no-zoom` - Endpoint that changes the tracking to use the audio model without adaptive zooming
    - `return`:
        - `"tracking"`: the enum corresponding to the AudioModelNoAdaptiveZoom
        - HTTP 200: the model has successfully been set to the AudioModelNoAdaptiveZoom

* __GET__ `/track/object` - Endpoint that changes the tracking to use the object tracking model
    - `return`:
        - `"tracking"`: the enum corresponding to the WaitObjectAudioModel
        - HTTP 200: the model has successfully been set to the WaitObjectAudioModel

* __GET__ `/track/hybrid` - Endpoint that changes the tracking to use the hybrid model
    - `return`:
        - `"tracking"`: the enum corresponding to the hybrid model
        - HTTP 200: the model has successfully been set to the hybrid model

