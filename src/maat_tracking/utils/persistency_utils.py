import json
import numpy as np

class CustomEncoder(json.JSONEncoder):
    """Class and method help with JSON encoding of a np.ndarray,
    as it is not JSON serializable by default"""
    def default(self, o):
        if isinstance(o, (np.ndarray, np.generic)):
            return o.tolist()
        return o.__dict__
