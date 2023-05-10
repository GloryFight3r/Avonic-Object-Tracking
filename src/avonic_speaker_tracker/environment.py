import numpy as np

class Environment:
    plane = None

    def __init__(self):
        self.plane = Plane()

    def add_point_to_plane(self, point: (np.array, np.array)):
        """ Adds a point to the plane.

            Parameters:
                point: the left side of the tuple is the camera direction and the right side is the microphone direction.
        """
        self.plane.add_point(point)

    def reset_plane(self):
        self.plane = Plane()


class Plane:
    # amount of points to define the plane
    size = None
    points = None

    def __init__(self, size=3):
        self.size = size
        self.points = []

    def add_point(self, point: (np.array, np.array)):
        self.points.insert(0, point)
        self.points = self.points[:self.size]
