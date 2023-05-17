import numpy as np

def angle_between_vectors(p: np.array, q: np.array) -> float:
    return p.dot(q) / (np.linalg.norm(p) * np.linalg.norm(q))
