import numpy as np
import math

from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_camera_api.converter import vector_angle
from avonic_speaker_tracker.audio_model.calibration import Calibration
from avonic_speaker_tracker.utils.coordinate_translation import translate_microphone_to_camera_vector
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel

class ObjectModel():
    """ Class with helper methods for calibration tracking. This class has to be extended
        so that track_object can be implemented. This facilitates using
        different strategies of dealing with both the object detection and the audio detection.
    """

    def __init__(self, cam_api: CameraAPI, mic_api: MicrophoneAPI, resolution: np.ndarray = np.array([0, 0])):
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.resolution = resolution

    def get_center_box(self, boxes: [np.array]):
        """ Gets the box closest to the center of the screen.

            params:
                boxes: an array of boxes represented as numpy arrays

            returns:
                box (np.array): the box closest to the center
        """
        get_center = lambda box: np.array([(box[0] + box[2])/2, (box[1] + box[3])/2])
        center = sorted(boxes,
                        key=lambda box: np.linalg.norm(get_center(box) - self.resolution/2))[0]
        return center

    def get_movement_to_box(self, current_box: list):
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

        cam_fov:np.ndarray = self.cam_api.calculate_fov()
        print(cam_fov, "cam-fov")

        angular_resolution = (cam_fov / self.resolution)
        print(angular_resolution, "res")

        rotate_angle = angular_resolution * distance_to_middle
        rotate_speed = self.calculate_speed(angular_resolution)
        print(rotate_angle, "Angle")

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
    time_without_movement = None

    def __init__(self, cam: CameraAPI, mic: MicrophoneAPI, resolution: np.ndarray, threshold: int,
                 filename = None):
        super().__init__(cam, mic)
        self.resolution = resolution
        self.threshold = threshold
        self.calibration = Calibration(filename=filename)
        self.calibration.load()
        self.prev_dir = np.array([0, 0, 1])
        self.time_without_movement = 0

    def track_object(self, current_box: list):
        if self.time_without_movement < 5:
            return

        speed, angle = self.get_movement_to_box(current_box)
        avg_angle = (angle[0] + angle[1]) / 2

        if abs(avg_angle) <= self.threshold:
            print("Moving!!!", str(avg_angle))
            self.cam_api.move_relative(speed[0], speed[1],\
                                angle[0], angle[1])
        else:
            print("Not moving!!!", str(avg_angle))

    def point(self):
        """ Points the camera towards the calculated direction from either:
        the presets or the continuous follower.
            Args:
                direct: the direction in which to point the camera
            Returns: the pitch and yaw of the camera and the zoom value
        """
        if self.speak_delay == 100:
            self.cam_api.direct_zoom(0)
            self.prev_dir[2]=0
            return self.prev_dir

        mic_direction = self.mic_api.get_direction()

        if isinstance(mic_direction, str):
            print(mic_direction)
            return self.prev_dir

        cam_vec = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                        mic_direction,
                                                        self.calibration.mic_height)

        vec_len = np.sqrt(cam_vec.dot(cam_vec))
        vec_len = min(vec_len,10.0)
        zoom_val = (int)((vec_len/10.0)*16000)

        direct = vector_angle(cam_vec)
        direct = [int(np.rad2deg(direct[0])), int(np.rad2deg(direct[1])), zoom_val]

        avg = abs(direct[0] - self.prev_dir[0])
        if avg >= self.threshold:
            self.time_without_movement = 0
        print("Time without movement")
        print(self.time_without_movement)

        diffX = math.fabs(self.prev_dir[0]-direct[0])*2
        diffY = math.fabs(self.prev_dir[1]-direct[1])*2

        speedX = (int)(13 + diffX/360*11)
        speedY = (int)(11 + diffY/120*9)

        speedX = min(speedX,24)
        speedY = min(speedY,20)

        if direct is None:
            return self.prev_dir

        if self.time_without_movement < 5:
            if self.prev_dir[0] != direct[0] or self.prev_dir[1] != direct[1]:
                self.cam_api.move_absolute(speedX, speedY, direct[0], direct[1])
            self.time_without_movement += 1

        if self.prev_dir[2] != direct[2]:
            self.cam_api.direct_zoom(direct[2])

        self.prev_dir = direct
        return direct

#class ThresholdCalibrationTracker(CalibrationTracker):
#    """ This class extends CalibrationTracker. It uses the strategy of using audio
#        tracking when the movement is big and object tracking when the movement is small.
#    """
#
#    # do not move the camera if camera is moved by more degrees than this threshold
#    threshold = None
#
#    def __init__(self, cam: CameraAPI, mic: MicrophoneAPI, resolution: np.ndarray, threshold: int):
#        super().__init__(cam, mic, resolution)
#        self.threshold = threshold
#
#    def track_object(self, current_box: list):
#        speed, angle = self.get_movement_to_box(current_box)
#        avg_angle = (angle[0] + angle[1]) / 2
#
#        if abs(avg_angle) <= self.threshold:
#            print("Moving!!!", str(avg_angle))
#            self.cam_api.move_relative(speed[0], speed[1],\
#                                angle[0], angle[1])
#        else:
#            print("Not moving!!!", str(avg_angle))
#
#    def track_audio(self, direct, prev_dir=(0.0, 0.0)):
#        """ Points the camera towards the calculated direction.
#            Args:
#                direct: the direction in which to point the camera
#                prev_dir: The previous direction to which the camera was pointing
#            Returns: the pitch and yaw of the camera and the zoom value
#        """
#        if direct is None:
#            return prev_dir
#        if prev_dir[0] != direct[0] or prev_dir[1] != direct[1]:
#            avg = (abs(direct[0] - prev_dir[0]) + abs(direct[1] - prev_dir[1])) / 2
#            if avg >= 0:
#                print("DIRECTION")
#                print(direct)
#                self.cam_api.move_absolute(24,20, direct[0], direct[1])
#            prev_dir = direct
#
#        return prev_dir
