import numpy as np


def cos_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Calculates cosine similarity between two vectors.
    Holds symmetric property, value is in [-1, 1]
    -1 - most different, 1 - most similar
    https://en.wikipedia.org/wiki/Cosine_similarity

    Args:
        a: first vector [x, y, z]
        b: second vector [x, y, z]
    Returns:
        cosine similarity of a and b
    """
    if len(a.shape) > 2 or (a.shape[0] != 3) or (len(a.shape) == 2 and a.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    if len(b.shape) > 2 or (b.shape[0] != 3) or (len(b.shape) == 2 and b.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        raise ValueError("Impossible to get similarity with zero-vector")
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_most_similar_preset(current: np.ndarray, presets: list[np.ndarray]) -> int:
    """Finds index of the most similar preset in relation
    to the given vector in the list of presets.

    Args:
        current: current vector of microphone direction, to which try to find the most similar.
        presets: list of vectors pointing to the presets;

    Returns:
        index in the list of the most similar preset to the current vector
    """
    if len(presets) == 0:
        raise ValueError("Empty list of presets given")
    similarity = np.apply_along_axis(lambda x: cos_similarity(current, x), 1, np.array(presets))
    return int(np.argmax(similarity))
