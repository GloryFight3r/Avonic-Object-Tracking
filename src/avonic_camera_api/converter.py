import numpy as np


def angle_vector(alpha: int, beta: int) -> np.array:
    """ Convert pitch and yaw angles (radians) to a unit vector

    Args:
        alpha: yaw - horizontal angle in rad
        beta: pitch - vertical angle in rad

    Returns:
        numpy 3d vector array in the form [x, y, z]
        looking towards positive z-axis, with the y-axis being the height
    """
    cosb = np.cos(beta)
    return np.array([np.sin(alpha) * cosb, np.sin(beta), np.cos(alpha) * cosb])


def vector_angle(v: np.array) -> (float, float):
    """ Convert directional vector to pitch and yaw angles (radians)

    Args:
        v: the vector [x, y, z] looking towards positive z, with y being the height

    Returns:
        alpha - horizontal angle, beta - vertical angle in rad
    """
    if len(v) != 3 or not type(v[0]) is np.float64:
        if type(v[0]) is float:
            np.float64(v)
        else:
            raise TypeError("vector must contain three floats")
    norm = np.linalg.norm(v)
    if norm == 0:
        raise Exception("vector not normalisable")
    vec = v / norm  # normalise
    beta = np.arcsin(vec[1])
    cosb = np.cos(beta)
    alpha = np.arcsin(vec[0]/cosb)
    return alpha, beta
