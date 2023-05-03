'''
TODO: when we have access to microphone it should be made functional
Currently returns the two angles that are preset
'''


'''
Returns the azimuth of the direction 
from which the sound comes from 
'''
def get_azimuth(azimuth: int) -> int:


    if not type(azimuth) is int:
        raise Exception("Azimuth should be integer")

    return azimuth

'''
Returns the elevation of the direction 
from which the sound comes from 
'''
def get_elevation(elevation: int) -> int:

    if not type(elevation) is int:
        raise Exception("Elevation should be integer")
    return elevation