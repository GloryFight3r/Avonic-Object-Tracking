import numpy as np
import math
import cv2

from avonic_speaker_tracker.audio_model.AudioModel import AudioModel
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_camera_api.camera_control_api import CameraAPI

from avonic_speaker_tracker.utils.coordinate_translation \
    import translate_microphone_to_camera_vector
from avonic_speaker_tracker.object_model.ObjectModel import ObjectModel
from avonic_speaker_tracker.audio_model.calibration import Calibration
from avonic_speaker_tracker.object_model.yolov8 import YOLOPredict
from avonic_camera_api.converter import vector_angle
from avonic_camera_api.footage import FootageThread

class WaitObjectAudioModel(ObjectModel, AudioModel):
    """ This class extends CalibrationTracker. It uses the strategy of waiting till
        the microphone doesn't detect large movements and then uses object tracking
        till the microphone detects big movements again.
    """
    def __init__(self, cam: CameraAPI, mic: MicrophoneAPI,
                 resolution: np.ndarray, threshold: int,
                 nn: YOLOPredict, stream: FootageThread,
                 filename = ""):
        super().__init__(cam, mic, stream, nn, resolution)

        # the degrees below which object tracking moves
        self.threshold = threshold

        # the calibration file needed for AudioModel
        self.calibration = Calibration(filename=filename)
        self.calibration.load()

        # the latest camera direction
        self.prev_dir = np.array([0, 0, 1])

        # the amount of iterations of small or no camera movements
        self.time_without_movement = 0

        # how how time_without_movement has to be before object tracking starts
        self.wait = 10

        # the amount of iterations without sound
        self.speak_delay = 0


    def track_object(self):
        # read the fream from the footage thread
        im_arr = np.frombuffer(self.stream.buffer.raw[:self.stream.buflen.value], np.byte)
        frame = cv2.imdecode(im_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return

        # get the bounding box to center on
        boxes = self.nn.get_bounding_boxes(frame)
        current_box = self.get_center_box(boxes)

        # get the movement to this box
        speed, angle = self.get_movement_to_box(current_box)

        # calculate the angle between the current position and the position to move to
        avg_angle = (angle[0]**2 + angle[1]**2)**0.5

        # only move if this angle is smaller than the threshold
        # the *3 can be adapted to optimize object tracking
        if abs(avg_angle) <= self.threshold*3:
            self.cam_api.move_relative(speed[0], speed[1],\
                                angle[0], angle[1])

    def point(self) -> bool:
        """ Points the camera towards the calculated direction from either:
        the presets or the continuous follower.
            Args:
                direct: the direction in which to point the camera
            Returns: a boolean whether or not object tracking should start
        """
        start_object_tracking = False

        # zoom out if the there has been no sound for 100 iterations
        if self.speak_delay == 100:
            self.cam_api.direct_zoom(0)
            self.prev_dir[2]=0
            return start_object_tracking

        mic_direction = self.mic_api.get_direction()

        if isinstance(mic_direction, str):
            print(mic_direction)
            return start_object_tracking

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


        avg_angle = ((direct[0] - self.prev_dir[0])**2 + (direct[1] - self.prev_dir[1])**2)**0.5
        #avg_angle = abs(direct[0] - self.prev_dir[0])
        if avg_angle >= self.threshold:
            # reset the time_without_movement if we move above the threshold
            self.time_without_movement = 0
            start_object_tracking = False

        diffX = math.fabs(self.prev_dir[0]-direct[0])*2
        diffY = math.fabs(self.prev_dir[1]-direct[1])*2

        speedX = (int)(13 + diffX/360*11)
        speedY = (int)(11 + diffY/120*9)

        speedX = min(speedX,24)
        speedY = min(speedY,20)

        if direct is None:
            return start_object_tracking

        if self.time_without_movement < self.wait:
            if self.prev_dir[0] != direct[0] or self.prev_dir[1] != direct[1]:
                try:
                    self.cam_api.move_absolute(speedX, speedY, direct[0], direct[1])
                except AssertionError as e:
                    print(e)
        elif self.time_without_movement == self.wait:
            start_object_tracking = True
        self.time_without_movement += 1

        if self.prev_dir[2] != direct[2]:
            self.cam_api.direct_zoom(direct[2])

        self.prev_dir = direct
        return start_object_tracking
