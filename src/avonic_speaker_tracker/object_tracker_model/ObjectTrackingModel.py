from typing_extensions import override
import numpy as np
import math

from avonic_camera_api.footage import FootageThread
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from object_tracker.yolov2 import YOLOPredict
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_speaker_tracker.audio_model.calibration import Calibration
from avonic_speaker_tracker.utils.coordinate_translation\
    import translate_microphone_to_camera_vector
from avonic_camera_api.converter import vector_angle

class HybridTracker(TrackingModel):
    # last bounding box we were tracking
    last_tracked = None

    def __init__(self, filename:str, bbox: YOLOPredict, cam_footage:FootageThread):
        # load the calibration
        self.calibration = Calibration(filename=filename)
        self.calibration.load()

        self.bbox = bbox # the neural network which finds the bounding boxes from a frame

        self.cam_footage = cam_footage # camera footage that returns frames

    @override
    def point(self, mic_api: MicrophoneAPI, cam_api: CameraAPI):
        """ 
        Overrides the point method from TrackingModel. This method uses both
        object tracking and the audio speaker tracking in order to achieve
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
        Args:
            mic_api: API of the microphone
            cam_api: API of the camera
        """
        # get information about current speaker
        if mic_api.is_speaking(): # he is currently speaking

            # Get the speaker direction
            mic_direction:np.ndarray | None = mic_api.get_direction()
            
            # if the mic_direction is a str, then there is some problem with the microphone API
            if isinstance(mic_direction, str):
                print(mic_direction)
                return
            
            # translate the microphone direction to a camera direction using the calibration
            # information
            cam_vec:np.ndarray = translate_microphone_to_camera_vector(-self.calibration.mic_to_cam,
                                                        mic_direction,
                                                        self.calibration.mic_height)

            # transform the 3D vector to a pan and tilt numpy array
            cam_angles:np.ndarray = np.array(vector_angle(cam_vec))

            # calculate the current FoV so that we can determine if the camera direction
            # we should look to is current visible on the screen
            cur_fov:np.ndarray = cam_api.calculate_fov() / 180.0 * math.pi

            # transform the 3D vector to a pan and tilt numpy array
            cur_angle:np.ndarray = vector_angle(cam_api.get_direction())

            # if the point that the camera has to turn to is on the screen, we need to choose
            # the bounding box of the most likely speaker
            if  cam_angles[0] - (cur_fov[0] / 2) <= cur_angle[0] <= cam_angles[0] + (cur_fov[0] / 2) \
                and \
                cam_angles[1] - (cur_fov[1] / 2) <= cur_angle[1] <= cam_angles[1] + (cur_fov[0] / 2):

                # get all the bounding boxes from the current frame
                all_boxes:list[np.ndarray] = self.bbox.get_bounding_boxes(self.cam_footage.get_frame())
                
                # from the current angle subtract the camera angle minus half of the current FoV,
                # so that we can get the distance from the left most angle we can see, to the 
                # place we should be looking to
                # after that we divide this by the current FoV, so we can get it as a ratio
                # and finally multiply this ratio by the screen resolution, so we can find which
                # pixel on the screen the camera direction corresponds to
                pixels:np.ndarray = np.array(((cur_fov - (cam_angles - (cur_fov / 2))) / cur_fov)\
                    * self.cam_footage.resolution, dtype='int')
                
                # find nearest box we should be tracking
                speaker_box:np.ndarray | None = self.find_box(all_boxes, pixels)

                if speaker_box == None:
                    # no speakers on the screen, we make no adjustments
                    return
                
                # set this box as the last tracked box
                self.last_tracked = speaker_box
                
                # get the speed and rotation angle the camera should make
                ret: tuple[np.ndarray, np.ndarray] = self.get_movement_to_box(speaker_box, cam_api)
            
                rotate_speed:np.ndarray = ret[0]
                rotate_angle:np.ndarray = ret[1]

                # rotate the camera
                cam_api.move_relative(rotate_speed[0], rotate_speed[1],\
                                      rotate_angle[0], rotate_angle[1])
            else:
                # otherwise turn the camera towards him
                
                # TODO possibly fix the speed
                cam_api.move_absolute(20, 20, cam_angles[0], cam_angles[1])

        else:
            # if there is a person we have previously tracked, continue tracking him
            
            # get all the bounding boxes from the current frame
            all_boxes:list[np.ndarray] = self.bbox.get_bounding_boxes(self.cam_footage.get_frame())

            # find the box from all_boxes that has the most surface area in common
            new_box = self.find_most_common_area(self.last_tracked, all_boxes)

            # set the last tracked box to new_box
            self.last_tracked = new_box

            # get the movement we have to make
            ret:tuple[np.ndarray, np.ndarray] = self.get_movement_to_box(speaker_box, cam_api)
            
            rotate_speed:np.ndarray = ret[0]
            rotate_angle:np.ndarray = ret[1]

            # move the camera according to that rotation speed and angle
            cam_api.move_relative(rotate_speed[0], rotate_speed[1],\
                                  rotate_angle[0], rotate_angle[1])

            
    def find_most_common_area(self, current_box: np.ndarray, all_boxes: list[np.ndarray])-> np.ndarray | None:
        """ Finds the box that has the most surface area in common with current_box

        Args:
            current_box: the current bounding box in the format np.array[left top right bottom]
            all_boxes: list of bounding boxes in the format np.array[left top right bottom]

        Returns:
            The bounding box that has the most surface area in common with current_box - np.array[left top right bottom] or None if
            all_boxes is empty
        """
        # if there are no bounding boxes in the list, return None
        if len(all_boxes) == 0:
            return None

        answer_box = None
        most_area = 0

        for bbox in all_boxes:
            # calculate the overlapping area
            x_side = min(current_box[2], bbox[2]) - max(current_box[0], bbox[0])
            y_side = min(current_box[1], bbox[1]) - max(current_box[3], bbox[3])

            # if there is overlap on both of the dimensions
            if x_side > 0 and y_side > 0:
                cur_area =  x_side * y_side

                if cur_area > most_area:
                    answer_box = bbox
                    most_area = cur_area
            
        return answer_box

    def find_box(self, all_boxes:list[np.ndarray], pixels:np.ndarray)->np.ndarray | None:
        """ From the list of all boxes, we choose the one that has its center closest
        to the pixel

        Args:
            all_boxes: list of numpy arrays in the format [left top right bottom]
            pixels: numpy array in the format [x, y]

        Returns:
            A numpy array that represents the bounding box we have chosen in the format
            [left top right bottom]
        """
        # we pick the one that has its center closest to pixels
        min_dist = float('inf')
        best_box = None
        
        for box in all_boxes:
            center = np.array([box[2] - box[0], box[1] - box[3]])

            # squared distance to the center
            cur_dist = (center - pixels) ** 2
            if cur_dist < min_dist:
                min_dist = cur_dist
                best_box = box

        return best_box

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

    def calculate_speed(self, rotate_angle:np.ndarray)->np.ndarray:
        """ Calculate the speed with which we want to make the camera 
            adjustment

        Args:
            rotate_angle: the rotation angle we will be performing

        Returns:
            2D numpy array that represents the pan and tilt rotation speed accordingly
        """
        return np.array([20, 20])
