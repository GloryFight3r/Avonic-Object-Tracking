# Presets API

## Description
`preset_locations_endpoints.py` contains all the source code of the available endpoints. Below you find the list of available endpoints. Their declaration is defined in `__init__.py`. They take `integration` as a parameter, to access methods for exchange with camera and the microphone.

# API

* __POST__ `/preset/add` - Endpoint that saves a preset into the preset collection.
    - `form`:
        - `"preset-name"`: Unique string representing the name of the preset.
        - `"camera-direction-alpha"`: Float from -170 - 170 representing the yaw of the camera
        - `"camera-direction-beta"`: Float from -30 - 90 representing the pitch of the camera
        - `"camera-zoom-value"`: Integer with the zoom value (0-16384)
        - `"mic-direction-x"`: Float representing the x-coordinate of the direction vector.
        - `"mic-direction-y"`: Float representing the y-coordinate of the direction vector.
        - `"mic-direction-z"`: Float representing the z-coordinate of the direction vector.
    - `return`:
        - HTTP 200: success, empty message
        - HTTP 400: invalid supplied values, empty message

* __POST__ `/preset/edit` - Endpoint that edits a preset in the preset collection.
    - `form`:
        - `"preset-name"`: String representing the name of the preset
        - `"camera-direction-alpha"`: Float from -170 - 170 representing the yaw of the camera
        - `"camera-direction-beta"`: Float from -30 - 90 representing the pitch of the camera
        - `"camera-zoom-value"`: Integer with the zoom value (0-16384)
        - `"mic-direction-x"`: Float representing the x-coordinate of the direction vector.
        - `"mic-direction-y"`: Float representing the y-coordinate of the direction vector.
        - `"mic-direction-z"`: Float representing the z-coordinate of the direction vector.
    - `return`:
        - HTTP 200: success, empty message
        - HTTP 400: invalid supplied values, empty message

* __POST__ `/preset/remove` - Endpoint that removes the given preset from the preset collection.
    - `form`:
        - `"preset-name"`: string name for the preset
    - `return`:
        - HTTP 200: success, empty message
        - HTTP 400: invalid supplied values, empty message

* __GET__ `/preset/get-list` - Endpoint that returns the list of all saved presets.
    - `return`:
        `- "preset-list"`: list of all presets in a json format

* __GET__ `/preset/info/<preset_name>` - Endpoint that returns information about a given preset.
    - `return`:
        - In case of success:
            - HTTP 200
            - "position-alpha-value": Float from -170 - 170 representing the yaw of the camera
            - "position-beta-value": Float from -30 - 90 representing the pitch of the camera
            - "zoom-value": Integer with the zoom value (0-16384)
            - "microphone-direction": a 3D vector (array) of floats [x, y, z]
        - In case of an error:
            - HTTP 400, empty message

* __GET__ `/preset/point` - Endpoint that points the camera to the closest preset available.
        Performs movement.
    - `return`:
        - HTTP 200, empty message