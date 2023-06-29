# Camera API

## Description
`camera_endpoints.py` contains all of the source code of the available endpoints. Below you find the list of available endpoints. Their declaration is defined in `__init__.py`. They take `integration` as a parameter, to access methods for exchange with camera and the microphone.

# API

## Connection

 * __POST__ `/camera/address/set` - Endpoint that sets the camera network settings.
    - `form`:
        - `"camera-ip"`: the address of the connected camera
        - `"camera-port"`: the camera port
        - `"camera-http-port"`: the HTTP port of the camera
    - `return`:
        - HTTP code corresponds to the camera response:
            - `"message"`: description of the received response code from the camera
        -   Possible HTTP 400: invalid supplied values
            - `"message"`: "Invalid address!"
## Power

 * __POST__ `/camera/reboot` - Completely reboot the camera.
 * __POST__ `/camera/on` - Turn the camera (the sensor) on.
 * __POST__ `/camera/off` - Turn the camera (the sensor) off.

## Movement


 * __POST__ `/camera/move/home` - Endpoint to move the camera to its home direction `[0, 0, 1]`.
    - `return`:
        - HTTP code corresponds to the camera response:
            - `"message"`: description of the received response code from the camera
 * __POST__ `/camera/move/stop` - Endpoint to stop all the camera's movement.
    - `return`:
        - HTTP code corresponds to the camera response:
            - `"message"`: description of the received response code from the camera
 * __POST__ `/camera/move/relative` - Move the camera relative to the current position..
    - `form`:
        - `relative-speed-x`: Integer from 1 - 24, the pan speed.
        - `relative-speed-y`: Integer from 1 - 20, the tilt speed.
        - `relative-degrees-x`: Float from -170 - 170, the amount of degrees to pan by.
        - `relative-degrees-y`: Float from -30 - 90, the amount of degrees to tilt by.
    - `return`:
        - HTTP code corresponds to the camera response:
            - `"message"`: description of the received response code from the camera
        - Possible HTTP 400: assertion error of validity of supplied values
 * __POST__ `/camera/move/absolute` - Move the camera relative to the home position.
    - `form`:
        - `absolute-speed-x`: Integer from 1 - 24, the pan speed.
        - `absolute-speed-y`: Integer from 1 - 20, the tilt speed.
        - `absolute-degrees-x`: Float from -170 - 170, the amount of degrees to pan by.
        - `absolute-degrees-y`: Float from -30 - 90, the amount of degrees to tilt by.
    - `return`:
        - HTTP code corresponds to the camera response:
            - `"message"`: description of the received response code from the camera
        - Possible HTTP 400: assertion error of validity of supplied values
 * __POST__ `/camera/move/vector` - Move the camera to point towards a vector.
    - `form`:
        - `vector-speed-x`: Integer from 1 - 24, the pan speed.
        - `vector-speed-y`: Integer from 1 - 20, the tilt speed.
        - `vector-x`: Float representing the x-coordinate of the direction vector.
        - `vector-y`: Float representing the y-coordinate (height) of the direction vector.
        - `vector-z`: Float representing the z-coordinate of the direction vector.
    - `return`:
        - HTTP code corresponds to the camera response:
            - `"message"`: description of the received response code from the camera
        - Possible HTTP 400: assertion error of validity of supplied values

 * __POST__ `/camera/navigate` - Endpoint that navigates the camera so that the clicked pixel is centered in the frame
    - `form`:
        - `"x-pos"`: a float value in the range $[0, 1]$
        - `"y-pos"`: a float value in the range $[0, 1]$
    - `return`:
        - In case of an error:
            - `"message"`: the error that was thrown
            - HTTP 400: bad request, see "message" for more details
            - HTTP 409: conflict, in case the command to the camera got cancelled
            - HTTP 504: time out in the camera
        - In case of a success:
            - `"message"`: success message
            - HTTP 200: success code

## Zoom

 * __GET__ `/camera/zoom/get` - Endpoint to get the zoom value of the camera.
    - `return`:
        - In case of an error:
            - HTTP code corresponds to the camera response
            - `"message"`: description of the received response code from the camera
        - In case of success:
            - HTTP 200
            - `"zoom-value"`: Integer in range [0, 16384], the value of the zoom
 * __POST__ `/camera/zoom/set` - Endpoint to set the zoom value of the camera.
    - `form:`
        - `"zoom-value"`: Integer in range [0, 16384], the value of the zoom
    - `return`:
        - HTTP code corresponds to the camera response:
            - `"message"`: description of the received response code from the camera
        - Possible HTTP 400: assertion error of validity of supplied values


## Position

 * __GET__ `/camera/position/get` - Endpoint to get the current pan and tilt values of the camera.
    - `return`:
        - In case of an error:
            - HTTP code corresponds to the camera response
            - `"message"`: description of the received response code from the camera
        - In case of success:
            - HTTP 200
            - `"position-alpha-value"`: pan value of the camera
            - `"position-beta-value"`: tilt value of the camera



# How to add a new endpoint
* Go to `src/maat_web_app` folder of the project.
* Add a new function with a unique name to `camera_endpoints.py`
* Declare an endpoint in `__init__.py` that returns call of the function you have previously created.
