import pytest
import numpy as np

from avonic_speaker_tracker.environment import Environment, Plane

def generate_plane_sizes():
    return [1, 2, 3, 4, 10]

@pytest.mark.parametrize("sz", generate_plane_sizes())
def test_plane_add_point(sz):
    plane = Plane(sz)
    assert plane.size == sz
    assert len(plane.points) == 0
    p = (np.array([]), np.array([]))
    plane.add_point(p)
    assert plane.points[0] == p
    assert len(plane.points) == 1
    for i in range(sz):
        plane.add_point(p)
    assert len(plane.points) == sz

def test_environment_add_points():
    env = Environment()
    p = (np.array([]), np.array([]))
    env.add_point_to_plane(p)
    assert env.plane.points[0] == p
    assert len(env.plane.points) == 1

def test_environment_reset_plane():
    env = Environment()
    p = (np.array([]), np.array([]))
    env.add_point_to_plane(p)
    env.reset_plane()
    assert not env.plane.points
