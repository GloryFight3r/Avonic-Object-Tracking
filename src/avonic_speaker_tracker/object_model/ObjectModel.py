import numpy as np

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.footage import FootageThread
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.object_model.yolov8 import YOLOPredict

class ObjectModel():
    """ Class with helper methods for calibration tracking. This class has to be extended
        so that track_object can be implemented. This facilitates using
        different strategies of dealing with both the object detection and the audio detection.
    """

    def __init__(self, cam_api: CameraAPI, mic_api: MicrophoneAPI,
                 stream: FootageThread, nn: YOLOPredict,
                 resolution: np.ndarray = np.array([0, 0])):
        self.cam_api = cam_api
        self.mic_api = mic_api

        # the resolution of the camera frames
        self.resolution = resolution

        # the neural network to use for object detection
        self.nn = nn

        # the thread that reads the footage stream of the camera
        self.stream = stream

    def get_center_box(self, boxes: [np.array]):
        """ Gets the box closest to the center of the screen.

            params:
                boxes: an array of boxes represented as numpy arrays

            returns:
                box (np.array): the box closest to the center
        """
        def get_center(box):
            return np.array([(box[0] + box[2])/2, (box[1] + box[3])/2])

        center = sorted(boxes,
                        key=lambda box: np.linalg.norm(get_center(box) - self.resolution/2))[0]
        return center

    def get_movement_to_box(self, current_box: np.ndarray) -> tuple[np.ndarray, np.ndarray]:

        """
            Return the relative angle the camera has to move in order to be looking at the
            center of current_box

        Args:
            current_box: numpy array in the format [left top right bottom]

        Returns:
            tuple of numpy arrays which represent (camera_speed, camera_angles)
        """
        # current_box is in the format [left top right bottom] and want to use the format
        # [left bottom width height] so we change it
        # The height is divided by two so the upper half of the person's body is used
        current_box = [current_box[0], current_box[1], current_box[2], current_box[3]/2]
        bbox:np.ndarray = np.array([current_box[0],\
                         current_box[3],\
                         current_box[2] - current_box[0],\
                         current_box[1] - current_box[3]
        ])

        # calculate the middle of the box in the format [x, y]
        box_middles:np.ndarray = (np.array([bbox[2], bbox[3]]) / 2)\
            + np.array([bbox[0], bbox[1]])

        # calculate the middle of the screen
        screen_middles:np.ndarray = self.resolution / 2.0

        # find the distance from the screen middle to the box middle
        distance_to_middle:np.ndarray = screen_middles - box_middles

        # flip the sign of the x axis distance
        distance_to_middle[0] = -distance_to_middle[0]

        # calculate current FoV of the camera
        try:
            cam_fov:np.ndarray = self.cam_api.calculate_fov()
        except TypeError as e:
            print(e)
            return ([20, 20], [0, 0])

        # calculate how many degrees correspond to one pixel
        angular_resolution:np.ndarray = cam_fov / self.resolution

        # find the relative angle the camera must rotate so that it centers on the bounding box
        rotate_angle:np.ndarray = angular_resolution * distance_to_middle

        # TODO pick a good rotation speed according to the rotation angle it has to make
        rotate_speed:np.ndarray = self.calculate_speed(angular_resolution)

        return (rotate_speed, rotate_angle)


    def calculate_speed(self, rotate_angle: np.ndarray):
        return [20, 20]

    def track_object(self):
        pass
