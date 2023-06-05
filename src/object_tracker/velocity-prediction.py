import numpy as np
import time
from avonic_camera_api.footage import FootageThread
from avonic_speaker_tracker.preset_control import cos_similarity
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_camera_api.camera_control_api import CameraAPI
from object_tracker.yolov2 import YOLOPredict


class VelocityPrediction:
    prev_pos = None

    def __init__(self):
        pass

    def point(self, mic_api: MicrophoneAPI, cam_api: CameraAPI):
        all_boxes = [[], []]

        # get information about current speaker
        if self.mic_api.is_speaking():
            # if he is on the screen then start tracking his box
            
            # cur_dir - new_dir
            # find position on screen
            cur_fov = cam_api.calculate_fov()
            cur_angle = cam_api.get_direction()
            self.mic_api.

            # now there is the problem that we might have to change the speaker box

            # if the sum goes over the needed one, we change the followed box
            # otherwise we follow the current box

            # otherwise turn the camera towards him, and set looking for speaker to true
        else:
            # if there is a person we have previously tracker, continue tracking him
            # get the bounding box that is closest to his previous position


            pass
