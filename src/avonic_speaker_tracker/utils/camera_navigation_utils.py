import numpy as np

from avonic_camera_api.camera_control_api import CameraAPI

def get_movement_to_box(self, current_box: np.ndarray, cam_api:CameraAPI) -> \
    tuple[np.ndarray, np.ndarray]:

    """ 
        Return the relative angle the camera has to move in order to be looking at the 
        center of current_box
        
    Args:
        current_box: numpy array in the format [left top right bottom]
        cam_api: API of the camera 

    Returns:
        tuple of numpy arrays which represent (camera_speed, camera_angles)
    """
    # current_box is in the format [left top right bottom] and want to use the format
    # [left bottom width height] so we change it
    bbox:np.ndarray = np.array([current_box[0],\
                     current_box[3],\
                     current_box[2] - current_box[0],\
                     current_box[1] - current_box[3]
    ])

    # calculate the middle of the box in the format [x, y]
    box_middles:np.ndarray = (np.array([bbox[2], bbox[3]]) / 2)\
        + np.array([bbox[0], bbox[1]])

    # calculate the middle of the screen
    screen_middles:np.ndarray = self.cam_footage.resolution / 2.0

    # find the distance from the screen middle to the box middle
    distance_to_middle:np.ndarray = screen_middles - box_middles

    # flip the sign of the x axis distance
    distance_to_middle[0] = -distance_to_middle[0]

    # calculate current FoV of the camera
    cam_fov:np.ndarray = cam_api.calculate_fov()

    # calculate how many degrees correspond to one pixel
    angular_resolution:np.ndarray = (cam_fov / self.cam_footage.resolution)

    # find the relative angle the camera must rotate so that it centers on the bounding box
    rotate_angle:np.ndarray = angular_resolution * distance_to_middle
    
    # TODO pick a good rotation speed according to the rotation angle it has to make
    rotate_speed:np.ndarray = self.calculate_speed(angular_resolution)

    return (rotate_speed, rotate_angle)

