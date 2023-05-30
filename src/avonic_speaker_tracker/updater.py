from time import sleep
from threading import Thread
import requests
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.preset import PresetCollection
from avonic_speaker_tracker.pointer import point
from avonic_speaker_tracker.calibration import Calibration


class UpdateThread(Thread):
    loop = None
    # Custom thread class use a skeleton
    def __init__(self, event, url: str, cam_api: CameraAPI, mic_api: MicrophoneAPI, preset_locations: PresetCollection, calibration: Calibration, preset_use: bool):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super().__init__()
        self.event = event
        self.value = None
        self.url = 'http://' + url
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.preset_locations = preset_locations
        self.calibration = calibration
        self.preset_use = preset_use

    def run(self):
        """ Actual body of the thread.
        Method should start with self.event.wait() to make sure that on
        start of the thread with false flag, body of the while-loop is not executed.
        """
        prev_dir = [0.0, 0.0]
        thread_mic = Thread(target=self.send_update, args=(self.get_mic_info, '/update/microphone'))
        thread_mic.start()
        thread_cam = Thread(target=self.send_update, args=(self.get_cam_info, '/update/camera'))
        thread_cam.start()
        while not self.event.is_set():
            if self.value is None:
                print("STOPPED BECAUSE CALIBRATION IS NOT SET")
                sleep(5)
                continue

            if len(self.preset_locations.get_preset_list()) == 0 and self.preset_use :
                print("No locations preset")
            else :
                prev_dir = point(self.cam_api, self.mic_api, self.preset_locations, self.preset_use, self.calibration, prev_dir)

            self.value += 1
            sleep(0.3)
        print("Exiting thread")

    def set_calibration(self, value):
        self.value = value

    def get_mic_info(self):
        """ Get information about the microphone.
        """
        return {
            "microphone-direction": list(self.mic_api.get_direction()),
            "microphone-speaking": self.mic_api.is_speaking()
        }

    def get_cam_info(self):
        """ Get the direction of the camera.
        """
        direction = self.cam_api.get_direction()
        return {
            "camera-direction": {
                "position-alpha-value": direction[0],
                "position-beta-value": direction[1]
            },
            "zoom-value": self.cam_api.get_zoom(),
            "camera-video": self.cam_api.video
        }

    def send_update(self, data, path: str):
        """ Send an HTTP request to the flask server to update the webpages.

        Args:
            data: The data in dictionary format
            path: The path to send to
        """
        while not self.event.is_set():
            d = data()
            response = requests.post(self.url + path, json=d)
            if response.status_code != 200:
                print("Could not update flask at path " + path)
            sleep(0.3)
