# Settings API

## Description
`settings_endpoints.py` contains all the source code of the available endpoints. Below you find the list of available endpoints. Their declaration is defined in `__init__.py`. They take `integration` as a parameter, to access methods for exchange with camera and the microphone.

# API

* __GET__ `/settings/get` - Endpoint that returns the settings that are currently active.
    - `return`:
        - `"camera-ip"`: the address of the connected camera
        - `"camera-port"`: the port of the connected camera
        - `"microphone-ip"`: the address of the connected microphone
        - `"microphone-port"`: the port of the connected microphone
        - `"microphone-thresh"`: an int value between -90 and 0 representing the preferred volume threshold
        - `"filepath"`: a string representing the folder in which the settings file is stored
        - HTTP 200: successfully gotten the settings

* __POST__ `/settings/set` - Endpoint that sets the settings to the ones given.
    - `form`:
        - `"camera-ip"`: the address of the camera to connect to
        - `"camera-port"`: the port of the camera to connect to
        - `"microphone-ip"`: the address of the microphone to connect to
        - `"microphone-port"`: the port of the microphone to connect to
        - `"microphone-thresh"`: an int value between -90 and 0 representing the preferred volume threshold
        - `"filepath"`: a string representing the folder in which to store the settings file
    - `return`:
        - In case of an error:
            - `"message"`: description of the error that was caught
            - HTTP 400: either the threshold or the filepath were not given correctly
            - HTTP 500: an error occurred while writing to the settings file
        - In case of success:
            - HTTP 200: success code