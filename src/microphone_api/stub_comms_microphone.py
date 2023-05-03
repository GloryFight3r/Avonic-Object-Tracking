'''
TODO: when we have access to microphone it should be made functional
Currently returns the two angles that are preset
'''

def get_azimuth(azimuth: int) -> int:


    if not type(azimuth) is int:
        raise Exception("Azimuth should be integer")

    return azimuth

def get_elevation(elevation: int) -> int:

    if not type(elevation) is int:
        raise Exception("Elevation should be integer")
    return elevation