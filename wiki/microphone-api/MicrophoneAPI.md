## Description
The MicrophoneAPI class contains an instance of [MicrophoneSocket](./wiki/microphone-api/MicrophoneSocket.md)
which contains a connect to the microphone. The MicrophoneAPI class uses the
MicrophoneSocket methods to send requests to the microphone.

# List of commands

### Constraints:

## set_address(address:tuple[str, int])
connects to the microphone corresponding to the given *address*

## get_azimuth() -> float
gets the azimuth of the beam from the microphone towards the detected sound

## get_elevation() -> float
gets the elevation of the beam from the microphone towards the detected sound

## get_direction() -> np.ndarray
gets both the azimuth and the elevation of the beam from the microphone towards
the detected sound and turns it into a vector

## vector() -> np.ndarray
returns the vector of the latest elevation and azimuth recorded by
*get_azimuth*, *get_elevation* or *get_direction*

## is_speaking() -> bool
returns a boolean indicating whether a sound is being detected with a volume
above the threshold defined in the [settings](LINK TO SETTINGS). If anything
goes wrong with the communication of the microphone, this method returns an
error message in the form of the string
