'''
TODO: when we have access to microphone it should be made functional
Currently returns the two angles that are preset
'''

class MicrophoneAPI:

    def __init__(self):
        self.microphone = microphone

    '''
    Returns the azimuth of the direction
    from which the sound comes from
    :param azimuth: currently preset angle
    :returns: the azimuth angle from microphone
    '''
    def get_azimuth(self,azimuth: int) -> int:

        if not type(azimuth) is int:
            raise Exception("Azimuth should be integer")

        return azimuth

    '''
    Returns the elevation of the direction
    from which the sound comes from
    :param elevation: currently preset angle
    :returns: the elevation angle from microphone
    '''
    def get_elevation(self,elevation: int) -> int:

        if not type(elevation) is int:
            raise Exception("Elevation should be integer")
        return elevation

    def set_height(self, height: float):
        """
        Sets the height of the microphone.

            Parameters:
                height (float): the new height
        """
        self.microphone.set_height(height)
