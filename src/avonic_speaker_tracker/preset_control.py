import numpy as np

def cos_similarity(a: np.array, b: np.array) -> float:
    """Calculates cosine similarity between two vectors.
    Holds symmetric property, value is in [-1, 1]
    -1 - most different, 1 - most similar
    https://en.wikipedia.org/wiki/Cosine_similarity

    :param a: first vector [x, y, z]
    :param b: second vector [x, y, z]
    :returns: cosine similarity of a and b
    """
    if len(a.shape) > 2 or (a.shape[0] != 3) or (len(a.shape) == 2 and a.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    if len(b.shape) > 2 or (b.shape[0] != 3) or (len(b.shape) == 2 and b.shape[1] != 1):
        raise TypeError("Not a 3D vector")
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        raise Exception("Impossible to get similarity with zero-vector")
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def find_most_similar_preset(current: np.array, presets: list[np.array]) -> int:
    """Finds index of the most similar preset in relation to the given vector in the list of presets.

    :param current: current vector of microphone direction, to which try to find the most similar.
    :param presets: list of vectors pointing to the presets;
    :returns: index in the list of the most similar preset to the current vector
    """
    if len(presets) == 0:
        raise Exception("Empty list of presets given")
    similartity = np.apply_along_axis(lambda x: cos_similarity(current, x), 1, np.array(presets))
    return np.argmax(similartity)
