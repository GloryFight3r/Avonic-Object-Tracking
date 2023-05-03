import numpy as np


def angle_vector(alpha: int, beta: int) -> np.array:
    return [alpha,beta,0]


def vector_angle(v: np.array) -> (int, int):
    return v[0], v[1]