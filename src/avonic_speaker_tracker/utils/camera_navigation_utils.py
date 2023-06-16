import numpy as np

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.footage import FootageThread

def get_movement_to_box(current_box: np.ndarray, cam_api:CameraAPI, cam_footage:FootageThread) -> \
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

    print(current_box, "CUR_BOX")
    print(cam_footage.resolution, "RES")

    assert 0 <= current_box[0] <= cam_footage.resolution[0]
    assert 0 <= current_box[2] <= cam_footage.resolution[0]

    assert 0 <= current_box[1] <= cam_footage.resolution[1]
    assert 0 <= current_box[3] <= cam_footage.resolution[1]

    box_width = current_box[2] - current_box[0]

    box_height = current_box[3] - current_box[1]

    assert 0 <= box_width <= cam_footage.resolution[0]
    assert 0 <= box_height <= cam_footage.resolution[1]

    # current_box is in the format [left top right bottom] and want to use the format
    # [left bottom width height] so we change it
    bbox:np.ndarray = np.array([current_box[0],\
                     current_box[1],\
                     current_box[2] - current_box[0],\
                     current_box[3] - current_box[1]
    ])

    # calculate the middle of the box in the format [x, y]
    box_middles:np.ndarray = (np.array([bbox[2], bbox[3]]) / 2)\
        + np.array([bbox[0], bbox[1]])

    print(cam_footage.resolution)
    assert 0 <= box_middles[0] <= cam_footage.resolution[0] and 0 <= box_middles[1] <= cam_footage.resolution[1]

    # calculate the middle of the screen
    screen_middles:np.ndarray = cam_footage.resolution / 2.0

    # find the distance from the screen middle to the box middle
    distance_to_middle:np.ndarray = box_middles - screen_middles# - box_middles

    # flip the sign of the x axis distance
    distance_to_middle[1] = -distance_to_middle[1]

    # calculate current FoV of the camera
    cam_fov:np.ndarray = cam_api.calculate_fov()

    # calculate how many degrees correspond to one pixel
    angular_resolution:np.ndarray = (cam_fov / cam_footage.resolution)

    # find the relative angle the camera must rotate so that it centers on the bounding box
    rotate_angle:np.ndarray = angular_resolution * distance_to_middle
    
    # TODO pick a good rotation speed according to the rotation angle it has to make
    rotate_speed:np.ndarray = calculate_speed(rotate_angle)

    return (rotate_speed, rotate_angle)

def calculate_speed(rotate_angle):
    """ Picks a rotation speed depending on the rotation angle

    Args:
        rotate_angle (): Current rotation angle

    Returns:
        Rotation speed for the next camera rotation
    """
    return np.array([20, 20])

