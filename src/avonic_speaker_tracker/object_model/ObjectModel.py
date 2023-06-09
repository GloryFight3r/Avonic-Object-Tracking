import math
import numpy as np

from avonic_camera_api.camera_control_api import CameraAPI
from avonic_camera_api.converter import vector_angle
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.audio_model.calibration import Calibration
from avonic_speaker_tracker.utils.coordinate_translation \
    import translate_microphone_to_camera_vector
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel

class ObjectModel():
    """ Class with helper methods for calibration tracking. This class has to be extended
        so that track_object can be implemented. This facilitates using
        different strategies of dealing with both the object detection and the audio detection.
    """

    def __init__(self, cam_api: CameraAPI, mic_api: MicrophoneAPI,
                 object_tracking_thread_event, resolution: np.ndarray = np.array([0, 0])):
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.object_tracking_thread_event = object_tracking_thread_event
        self.resolution = resolution
        self.speak_delay = 0
        self.wait = 10

    def get_center_box(self, boxes: [np.array]):
        """ Gets the box closest to the center of the screen.

            params:
                boxes: an array of boxes represented as numpy arrays

            returns:
                box (np.array): the box closest to the center
        """
        def get_center(box):
            return np.array([(box[0] + box[2])/2, (box[1] + box[3])/2])

        #center_point = np.array([self.resolution[0] / 2, self.resolution[1] / 3])
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
        cam_fov:np.ndarray = self.cam_api.calculate_fov()

        # calculate how many degrees correspond to one pixel
        angular_resolution:np.ndarray = cam_fov / self.resolution

        # find the relative angle the camera must rotate so that it centers on the bounding box
        rotate_angle:np.ndarray = angular_resolution * distance_to_middle

        # TODO pick a good rotation speed according to the rotation angle it has to make
        rotate_speed:np.ndarray = self.calculate_speed(angular_resolution)

        return (rotate_speed, rotate_angle)


    def calculate_speed(self, rotate_angle: np.ndarray):
        return [20, 20]


class WaitObjectAudioModel(ObjectModel, AudioModel):
    """ This class extends CalibrationTracker. It uses the strategy of waiting till
        the microphone doesn't detect large movements and then uses object tracking
        till the microphone detects big movements again.
    """

    # do not move the camera if camera is moved by more degrees than this threshold
    threshold = None
    #time_without_movement = None

    def __init__(self, cam: CameraAPI, mic: MicrophoneAPI, object_tracking_thread,
                 resolution: np.ndarray, threshold: int,
                 filename = ""):
        super().__init__(cam, mic, object_tracking_thread)
        self.resolution = resolution
        self.threshold = threshold
        self.calibration = Calibration(filename=filename)
        self.calibration.load()
        self.prev_dir = np.array([0, 0, 1])
        self.time_without_movement = 0

    def track_object(self, current_box: list):
        speed, angle = self.get_movement_to_box(current_box)
        avg_angle = (angle[0] + angle[1]) / 2

        if abs(avg_angle) <= self.threshold*3:
            self.cam_api.move_relative(speed[0], speed[1],\
                                angle[0], angle[1])

    def point(self):
        """ Points the camera towards the calculated direction from either:
        the presets or the continuous follower.
            Args:
                direct: the direction in which to point the camera
            Returns: the pitch and yaw of the camera and the zoom value
        """

        if self.speak_delay == 100:
            self.object_tracking_thread_event.value = 1
            self.cam_api.direct_zoom(0)
            self.prev_dir[2]=0
            return self.prev_dir
        elif self.speak_delay < 2:
            self.object_tracking_thread_event.value = 2

        mic_direction = self.mic_api.get_direction()

        if isinstance(mic_direction, str):
            print(mic_direction)
            return self.prev_dir

        try:
            cam_vec = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                        mic_direction,
                                                        self.calibration.mic_height)
            vec_len = np.sqrt(cam_vec.dot(cam_vec))
            vec_len = min(vec_len,10.0)
            zoom_val = (int)((vec_len/10.0)*16000)

            direct = vector_angle(cam_vec)
            direct = [int(np.rad2deg(direct[0])), int(np.rad2deg(direct[1])), zoom_val]

        except AssertionError:
            direct = self.prev_dir


        avg = abs(direct[0] - self.prev_dir[0])
        if avg >= self.threshold:
            self.time_without_movement = 0
            self.object_tracking_thread_event.value = 1

        diffX = math.fabs(self.prev_dir[0]-direct[0])*2
        diffY = math.fabs(self.prev_dir[1]-direct[1])*2

        speedX = (int)(13 + diffX/360*11)
        speedY = (int)(11 + diffY/120*9)

        speedX = min(speedX,24)
        speedY = min(speedY,20)

        if direct is None:
            return self.prev_dir

        if self.time_without_movement < self.wait:
            if self.prev_dir[0] != direct[0] or self.prev_dir[1] != direct[1]:
                self.cam_api.move_absolute(speedX, speedY, direct[0], direct[1])
        elif self.time_without_movement == self.wait:
            self.object_tracking_thread_event.value = 2
        self.time_without_movement += 1

        if self.prev_dir[2] != direct[2]:
            self.cam_api.direct_zoom(direct[2])

        self.prev_dir = direct
        return direct
