from time import sleep
from threading import Thread
import requests
import asyncio
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.preset import PresetCollection
from avonic_speaker_tracker.pointer import point


class CustomThread(Thread):
    # Custom thread class use a skeleton
    def __init__(self, event, url: str, cam_api: CameraAPI, mic_api: MicrophoneAPI, preset_locations: PresetCollection):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super(CustomThread, self).__init__()
        self.event = event
        self.value = None
        self.url = 'http://' + url
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.preset_locations = preset_locations

    def run(self):
        """ Actual body of the thread.
        Method should start with self.event.wait() to make sure that on
        start of the thread with false flag, body of the while-loop is not executed.
        """

        assert len(self.preset_locations.get_preset_list()) > 0
        prev_dir = [0,0]
        while not self.event.is_set():
            if self.value is None:
                print("STOPPED BECAUSE CALIBRATION IS NOT SET")
                sleep(5)
                continue
            print('Worker thread running...')


            prev_dir = point(self.cam_api,self.mic_api,self.preset_locations, prev_dir)

            self.value += 1
            #asyncio.run(self.send_update(self.get_mic_info(), '/update/microphone'))
            sleep(1)
        print('Worker closing down')

    def set_calibration(self, value):
        self.value = value

    def get_mic_info(self):
        """ Get information about the microphone.
        """
        return {
            "microphone-direction": list(self.mic_api.get_direction()),
            "microphone-speaking": self.mic_api.is_speaking()
        }

    def get_cam_direction(self):
        """ Get the direction of the camera.
        """
        return self.cam_api.get_direction()

    async def send_update(self, data: dict, path: str):
        """ Send an HTTP request to the flask server to update the webpages.

        Args:
            data: The data in dictionary format
            path: The path to send to
        """
        response = requests.post(self.url + path, json=data)
        if response.status_code != 200:
            print("Could not update flask at path " + path)
