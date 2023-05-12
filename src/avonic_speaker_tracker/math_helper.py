import numpy as np

def angle_between_vectors(p: np.array, q: np.array) -> float:
    # if not rounded, we get numbers like 1.0000000002 which breaks the cosine
    rounded = round(p.dot(q) / (np.linalg.norm(p) * np.linalg.norm(q)), 5)
    return np.arccos(rounded)
