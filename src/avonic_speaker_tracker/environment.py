import numpy as np

class Environment:
    plane = None

    def set_plane(self, plane: Plane):
        self.plane = plane

    def reset_plane():
        plane = None


class Plane:
    # amount of points to define the plane
    size = None
    points = None

    def __init__(self, size = 3):
        self.size = size
        self.points = [None] * size

    def add_point(p: (np.array, np.array)):
        points.insert(0, p)
        points = points[:size]
