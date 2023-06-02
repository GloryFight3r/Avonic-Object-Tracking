from time import sleep
from threading import Thread
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel

class UpdateThread(Thread):
    loop = None

    def __init__(self, event, url: str, cam_api: CameraAPI, mic_api: MicrophoneAPI, model: TrackingModel):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super().__init__()
        self.event = event
        self.value = None
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.model_in_use = model

    def run(self):
        """ Actual body of the thread.
        Method should start with self.event.wait() to make sure that on
        start of the thread with false flag, body of the while-loop is not executed.
        """
        prev_dir = [0.0, 0.0]
        speak_delay = 0
        while not self.event.is_set():
            if self.value is None:
                print("STOPPED BECAUSE CALIBRATION IS NOT SET")
                sleep(5)
                continue
            if self.mic_api.is_speaking():
                speak_delay = 0 
            else:
                speak_delay = speak_delay + 1 
            self.model_in_use.set_speak_delay(speak_delay)
            direct = self.model_in_use.point(self.cam_api, self.mic_api)

            self.value += 1
            sleep(0.05)
        print("Exiting thread")

    def set_calibration(self, value):
        """ Sets the calibration value.
        """
        self.value = value