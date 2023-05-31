from avonic_camera_api.camera_control_api import CameraAPI
import numpy as np

class BoxTracker:
    def __init__(self, cam: CameraAPI, resolution: np.ndarray):
        self.cam = cam
        self.resolution = resolution
    
    def camera_track(self, current_box: list):
        current_box[2] = current_box[2] - current_box[0]
        tmp = current_box[3]
        current_box[3] = current_box[1]
        current_box[1] = tmp
        current_box[3] = current_box[3] - current_box[1]
        box_middles = (np.array([current_box[2], current_box[3]]) / 2)\
            + np.array([current_box[0], current_box[1]])
        screen_middles = self.resolution / 2.0

        distance_to_middle = screen_middles - box_middles 
        distance_to_middle[0] = -distance_to_middle[0]
        print(distance_to_middle, "dist")

        cam_fov:np.ndarray = self.cam.calculate_fov()
        print(cam_fov, "cam-fov")

        angular_resolution = (cam_fov / self.resolution)
        print(angular_resolution, "res")

        rotate_angle = angular_resolution * distance_to_middle
        rotate_speed = self.calculate_speed(angular_resolution)
        print(rotate_angle, "Angle")

        self.cam.move_relative(rotate_speed[0], rotate_speed[1],\
                               rotate_angle[0], rotate_angle[1])

    def calculate_speed(self, rotate_angle:np.ndarray):
        return [20, 20]
