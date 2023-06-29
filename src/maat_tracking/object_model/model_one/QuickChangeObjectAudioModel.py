import time
import numpy as np
import cv2

from maat_tracking.object_model.ObjectModel import ObjectModel
from maat_tracking.object_model.yolov8 import YOLOPredict
from maat_tracking.utils.coordinate_translation \
    import translate_microphone_to_camera_vector
from maat_tracking.audio_model.calibration import Calibration
from maat_tracking.audio_model.AudioModel import AudioModel
from maat_camera_api.footage import FootageThread
from maat_camera_api.camera_control_api import CameraAPI
from maat_camera_api.camera_adapter import ResponseCode
from maat_camera_api.converter import vector_angle
from maat_microphone_api.microphone_control_api import MicrophoneAPI


class QuickChangeObjectAudio(ObjectModel, AudioModel):
    # last bounding box we were tracking
    last_tracked = np.array([0, 0, 0, 0])

    def __init__(self, cam: CameraAPI, mic: MicrophoneAPI, nn: YOLOPredict,
                 stream: FootageThread, filename: str):
        # load the calibration

        super().__init__(cam, mic, stream, nn, stream.resolution)
        self.calibration = Calibration(filename=filename)
        self.calibration.load()

    def point(self):
        """
        Overrides the point method from TrackingModel.
        This method uses both object tracking and the audio speaker tracking in order to achieve
        better accuracy. It works in the following way

        1. A speaker is talking
            Get speaker direction
            Transform to camera direction
            1.1 If camera direction is visible on screen
                Gen pixel on screen from the camera direction
                Find the bounding box that has the closest center to that pixel(Square distance)
                Start following that bounding box
            1.2 Otherwise, rotate the camera to that camera direction

        2. A speaker is not currently talking
            Get the last bounding box we were tracking on the last frame

            Get the bounding boxes from the current frame

            From all the bounding boxes from the current frame, pick the one that has the most pixel
            area in common with the last bounding box

            Start tracking this chosen bounding box
        """
        # get information about current speaker
        if self.mic_api.is_speaking():  # they are currently speaking
            # Get the speaker direction
            mic_direction: np.ndarray | None = self.mic_api.get_direction()

            # if the mic_direction is a str, then there is some problem with the microphone API
            if isinstance(mic_direction, str):
                return

            # translate the microphone direction to a camera direction using the calibration
            # information
            cam_vec: np.ndarray = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                                        mic_direction,
                                                                        self.calibration.mic_height)

            # transform the 3D vector to a pan and tilt numpy array
            cam_angles: np.ndarray = np.array(vector_angle(cam_vec))

            # calculate the current FoV so that we can determine if the camera direction
            # we should look to is current visible on the screen
            fov = self.cam_api.calculate_fov()
            if isinstance(fov, ResponseCode):
                return
            cur_fov: np.ndarray = np.deg2rad(fov)

            # transform the 3D vector to a pan and tilt numpy array
            cur_angle = self.cam_api.get_direction()
            if isinstance(cur_angle, ResponseCode):
                return

            cur_angle: np.ndarray = vector_angle(cur_angle)

            # if the point that the camera has to turn to is on the screen, we need to choose
            # the bounding box of the most likely speaker
            if cam_angles[0] - (cur_fov[0] / 2) <= cur_angle[0] <= cam_angles[0] + (cur_fov[0] / 2) \
                    and cam_angles[1] - (cur_fov[1] / 2) <= cur_angle[1] <= cam_angles[1] + (cur_fov[1] / 2):

                # get all the bounding boxes from the current frame
                all_boxes = self.nn.get_bounding_boxes(self.safely_get_frame())

                # only if we want to visualize
                # self.stream.set_bbxes(all_boxes)

                # (cam_angles - (cur_angle - (cur_fov / 2)) / cur_fov)

                # from the current angle subtract the camera angle minus half of the current FoV,
                # so that we can get the distance from the left most angle we can see, to the
                # place we should be looking to
                # after that we divide this by the current FoV, so we can get it as a ratio
                # and finally multiply this ratio by the screen resolution, so we can find which
                # pixel on the screen the camera direction corresponds to

                pixels: np.ndarray = np.array((cam_angles - (cur_angle - (cur_fov / 2))) / cur_fov)

                pixels[1] = 1 - pixels[1]

                pixels = np.array(pixels * self.resolution, dtype='int')

                # visualisation purposes
                # self.stream.pixel = pixels

                # find the nearest box we should be tracking
                speaker_box: np.ndarray | None = self.find_box(all_boxes, pixels)

                if speaker_box is None:
                    # no speakers on the screen, we make no adjustments
                    return

                # set this box as the last tracked box
                self.last_tracked = speaker_box
                # self.stream.focused_box = speaker_box

                # get the speed and rotation angle the camera should make
                ret: tuple[np.ndarray, np.ndarray] = self.get_movement_to_box(speaker_box)

                rotate_speed: np.ndarray = ret[0]
                rotate_angle: np.ndarray = ret[1]

                # rotate the camera
                try:
                    # rotation angle might not be possible
                    self.cam_api.move_relative(int(rotate_speed[0]), int(rotate_speed[1]),
                                               rotate_angle[0], rotate_angle[1])
                except AssertionError as e:
                    print(e)
            else:
                # otherwise turn the camera towards him

                rotate_angle: np.ndarray = np.rad2deg(cam_angles)
                try:
                    # rotate angle might not be possible for the camera(boundaries)
                    self.cam_api.move_absolute(20, 20, rotate_angle[0], rotate_angle[1])
                except AssertionError as e:
                    print(e)
        else:
            if self.last_tracked.size == 0:
                return
            # if there is a person we have previously tracked, continue tracking him

            # get all the bounding boxes from the current frame
            all_boxes = self.nn.get_bounding_boxes(self.safely_get_frame())

            # self.stream.set_bbxes(all_boxes)
            # find the box from all_boxes that has the most surface area in common
            new_box: np.ndarray | None = self.find_next_box(self.last_tracked, all_boxes)

            # self.stream.focused_box = new_box

            if new_box is None:
                self.last_tracked = np.array([0, 0, 0, 0])
                return

            # set the last tracked box to new_box
            self.last_tracked = new_box

            # get the movement we have to make
            ret: tuple[np.ndarray, np.ndarray] = self.get_movement_to_box(new_box)

            rotate_speed: np.ndarray = ret[0]
            rotate_angle: np.ndarray = ret[1]

            # move the camera according to that rotation speed and angle
            self.cam_api.move_relative(int(rotate_speed[0]), int(rotate_speed[1]),
                                       rotate_angle[0], rotate_angle[1])

    def safely_get_frame(self):
        im_arr = np.frombuffer(self.stream.buffer.raw[:self.stream.buflen.value], np.byte)
        frame = cv2.imdecode(im_arr, cv2.IMREAD_COLOR)

        return frame

    def find_next_box(self, current_box: np.ndarray,
                      all_boxes: list[np.ndarray]) -> np.ndarray | None:
        """ Finds the box that is most likely to be the same box
        from the previous frame by comparing distances to the box centers

        Args:
            current_box: the current bounding box in the format np.array[left bottom right top]
            all_boxes: list of bounding boxes in the format np.array[left bottom right top]

        Returns:
            The bounding box that has the most surface area in common
            with current_box - np.array[left top right bottom] or None if all_boxes is empty
        """
        # if there are no bounding boxes in the list, return None
        if len(all_boxes) == 0 or current_box is None:
            return None

        answer_box: np.ndarray | None = None
        closest_distance: float = float('inf')

        cur_box_middle: np.ndarray = np.array([(current_box[0] + current_box[2]) / 2,
                                               (current_box[1] + current_box[3]) / 2])

        for bbox in all_boxes:
            # calculate the middle pixel of the current box
            bbox_middle: np.ndarray = np.array([(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2])
            cur_dist: float = float(np.sum((bbox_middle - cur_box_middle) ** 2))

            if closest_distance > cur_dist:
                closest_distance = cur_dist
                answer_box = bbox

        return answer_box

    def find_box(self, all_boxes: list[np.ndarray], pixels: np.ndarray) -> np.ndarray | None:
        """ From the list of all boxes, we choose the one that has its center closest
        to the pixel

        Args:
            all_boxes: list of numpy arrays in the format [left bottom right top]
            pixels: numpy array in the format [x, y]

        Returns:
            A numpy array that represents the bounding box we have chosen in the format
            [left bottom right top]
        """
        # we pick the one that has its center closest to pixels
        min_dist = float('inf')
        best_box = None

        for box in all_boxes:
            center = np.array([(box[2] + box[0]) / 2, (box[1] + box[3]) / 2])

            # squared distance to the center
            cur_dist = np.sum((center - pixels) ** 2)
            if cur_dist < min_dist:
                min_dist = cur_dist
                best_box = box

        return best_box

    def sleep(self):
        time.sleep(1.3)
