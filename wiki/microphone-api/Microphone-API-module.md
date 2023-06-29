## Description
Microphone API module contains all of the functionality related to the Microphone. It contains:
* `microphone_adapter.py` - contains an adapter `MicrophoneSocket` that offers a
  general interface for connecting to the microphone and sending requests to it.
* `microphone_control_api.py` - contains an adapter that sends specified UDP
  requests to the microphone and formats the data from received requests.

## Use cases
Microphone API module is used in WebUI to obtain and display information about
the speaker, as well it is used in the Tracking module as it relies on
information from the microphone to find a speaker in the room.

## Related pages
* [MicrophoneAPI](./wiki/microphone-api/MicrophoneAPI.md)
* [MicrophoneSocket](./wiki/microphone-api/MicrophoneSocket.md)