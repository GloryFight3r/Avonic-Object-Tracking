# Calibration API

## Description
`calibration_endpoints.py` contains all of the source code of the available endpoints. Below you find the list of available endpoints. Their declaration is defined in `__init__.py`. They take `integration` as a parameter, to access methods for exchange with camera and the microphone.

# API

## Power

* __GET__ `/calibration/is-set` - Endpoint that checks whether the calibration is completed and all the needed vectors are calculated.
    - `return`:
        - `"is_set"`: boolean indicating whether calibration has been completed
        - HTTP 200: success code

* __POST__ `/calibration/reset` - Endpoint that resets the calibration to the default values
    - `return`:
        - HTTP 200: success code

* __GET__ `/calibration/camera` - Endpoint that calculates the relative coordinates of the camera in relation to the microphone.
    - `return`:
        - `"camera-coords"`: a 3D array of floats [x, y, z]
        - HTTP 200: successfully

* __GET__ `/calibration/number-of-calibrated` - Endpoint that returns the number of calibration points.
    - `return`:
        - `"speaker-points-length"`: the amount of speaker points that have been set
        - HTTP 200: successfully

* __POST__ `/calibration/add-direction-to-mic` - Endpoint that adds the direction from the camera towards the microphone to the calibration.
    - `return`:
        - In case of a success:
            - HTTP 200: success code
        - In case of an error:
            - `"message"`: the exact error message
            - HTTP 504: the error code if no direction could be gotten from the camera

* __POST__ `/calibration/add-directions-to-speaker` - Endpoint that adds the camera direction towards a new calibration point
    - `return`:
        - In case of a success:
            - HTTP 200: success code
        - In case of an error:
            - `"message"`: the exact error message
            - HTTP 504: the error code if no direction could be gotten from either the camera or the microphone
