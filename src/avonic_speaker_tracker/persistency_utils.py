import json
import numpy as np

class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (np.ndarray, np.generic)):
            return o.tolist()
        return o.__dict__