from avonic_camera_api.camera_control_api import CameraAPI
import numpy as np

class BoxTracker:
    def __init__(self, cam: CameraAPI, resolution: np.ndarray):
        self.cam = cam
        self.resolution = resolution
    
    def camera_track(self, current_box: list):
        """ The method should center the camera so that the bounding box's center is
            exactly at the middle of the screen

        Args:
            current_box: a list of four floats in the format 
                        [left top right bottom] which represent a bounding box
        """
        assert 0 <= current_box[0] <= self.resolution[0]
        assert 0 <= current_box[2] <= self.resolution[0]

        assert 0 <= current_box[1] <= self.resolution[1]
        assert 0 <= current_box[3] <= self.resolution[1]

        box_width = current_box[2] - current_box[0]

        box_height = current_box[1] - current_box[3]

        assert 0 <= box_width <= self.resolution[0]
        assert 0 <= box_height <= self.resolution[1]

        # we want our box to have the following format [X, Y], so we get the left and top coordinates
        # and we add half of the box_width and box_height to them

        box_middles = (np.array([box_width, box_height]) / 2)\
            + np.array([current_box[0], current_box[3]])

        assert 0 <= box_middles[0] <= self.resolution[0] and 0 <= box_middles[1] <= self.resolution[1]

        # half the resolution so that we get the center of the screen
        screen_middles = self.resolution / 2.0 

        # distance from the middle of the box to the center
        distance_to_middle = screen_middles - box_middles 
        distance_to_middle[0] = -distance_to_middle[0] # flip the sign of the horizontal angle

        cam_fov:np.ndarray = self.cam.calculate_fov() # get the current FoV

        angular_resolution = (cam_fov / self.resolution) # degrees per a single pixel

        # we get the rotation degrees by 
        #multiplying the resolution by the distance to the center
        rotate_angle = angular_resolution * distance_to_middle 

        # determine the speed we want to rotate at
        rotate_speed = self.calculate_speed(angular_resolution)

        # rotate the camera
        self.cam.move_relative(rotate_speed[0], rotate_speed[1],\
                               rotate_angle[0], rotate_angle[1])

    def calculate_speed(self, rotate_angle:np.ndarray):
        return [20, 20]
