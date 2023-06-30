# Microphone API
The complex microphone control API has been simplified to four methods.

## Description
`microphone_endpoints.py` contains all of the source code of the available endpoints. Below you find the list of available endpoints. Their declaration is defined in `__init__.py`. They take `integration` as a parameter, to access methods for exchange with camera and the microphone.

# API

## Settings
 * __POST__ `/microphone/height/set` - Endpoint to set the height of the microphone above the speaker plane.
    - `form`:
        - `"microphone-height"`: float representing value to be set
    - `return`:
        - HTTP 200:
            - `"microphone-height"`: with the value that was set
        - HTTP 504:
            - `"message"`: error message returned from the microphone
   - `param:microphone-height`: a float of how many meters above the speaker plane the microphone is located.
* __POST__ `/microphone/address/set` - Endpoint that sets the microphone network settings.
    - `form`:
        - `"microphone-ip"`: a string, the address of the microphone
        - `"microphone-port"`: the microphone port
    - `return`:
        - HTTP 200 or 400:
            - Text of the return message from the microphone
        - Possible HTTP 400: not valid supplied address or port:
            - `"message"`: "Invalid address!"

## Speaker
 * __GET__ `/microphone/direction` - Endpoint to get the current direction to the loudest noise in the room from the microphone
    - `return`:
        - HTTP 200:
            - `"microphone-direction"`: list with 3 float values representing direction of the speaker
        - HTTP 504:
            - `"message"`: error message returned from the microphone
 * __GET__ `/microphone/speaker/direction` -Endpoint to get the direction of the active speaker. Used for setting up presets and calibrating.
    Actively loops polling data from the microphone, waits for 5 seconds.
    If nobody has spoken in 5 seconds - returns current direction from the microphone.
    - `return`:
        - HTTP 200:
            - `"microphone-direction"`: list with 3 float values representing direction of the speaker
        - HTTP 504:
            - `"message"`: error message returned from the microphone
 * __GET__ `/microphone/speaking` - Retrieve whether somebody is speaking at the current moment, decided by minimum threshold.
    - `return`:
        - HTTP 200:
            - `"microphone-speaking"`: boolean representing is some someone speaking at the moment
        - HTTP 504:
            - `"message"`: error message returned from the microphone
