import numpy as np


def angle_vector(alpha: float, beta: float) -> np.ndarray:
    """ Convert pitch and yaw angles (radians) to a unit vector

    Args:
        alpha: yaw - horizontal angle in rad
        beta: pitch - vertical angle in rad

    Returns:
        numpy 3d vector array in the form [x, y, z]
        looking towards positive z-axis, with the y-axis being the height
    """
    cosb = np.cos(beta)
    return np.array([-np.sin(alpha) * cosb, np.sin(beta), np.cos(alpha) * cosb])


def vector_angle(v: np.ndarray) -> tuple[float, float]:
    """ Convert directional vector to pitch and yaw angles (radians)

    Args:
        v: the vector [x, y, z] looking towards positive z, with y being the height

    Returns:
        alpha - horizontal angle, beta - vertical angle in rad
    """
    if len(v) != 3 or not isinstance(v[0], np.float64):
        if isinstance(v[0], float):
            np.float64(v)
        else:
            raise TypeError("Vector must contain three floats")
    norm = np.linalg.norm(v)
    if norm == 0:
        raise ValueError("Vector not normalizable")
    vec = v / norm  # normalise
    home_vec = np.array([0, 0, 1])
    new_vec = np.array([vec[0], 0, vec[2]])
    new_vec /= np.linalg.norm(new_vec)
    alpha = np.arccos(home_vec.dot(new_vec))
    if vec[0] >= 0:
        alpha = -alpha

    beta = np.arcsin(vec[1])
    return alpha, beta
