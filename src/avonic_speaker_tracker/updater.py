from time import sleep
from threading import Thread
from ctypes import c_int
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.object_model.ObjectModel import ObjectModel

class UpdateThread(Thread):

    def __init__(self, event: c_int,
                 cam_api: CameraAPI, mic_api: MicrophoneAPI, model: TrackingModel,
                 filepath: str = ""):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super().__init__()
        self.event: c_int = event
        self.value: int = 0
        self.cam_api: CameraAPI = cam_api
        self.mic_api: MicrophoneAPI = mic_api
        self.model: TrackingModel = model
        self.filepath = filepath

    def run(self) -> None:
        """ Actual body of the thread.
        Continuously calls point method of the supplied model, to calculate the direction
        and point the camera towards it.

        Based on the self.preset_or_tracking, that is initialized in the constructor,
        the model is select upon the start of the thread.
        0 - AudioModel aka continuous tracking based on microphone information.
        1 - PresetModel aka presets, which selects the camera direction
        from the limited pool of options, based on cosine similarity.
        """
        speak_delay: int = 0
        while self.event.value != 0:
            if self.value is None:
                print("STOPPED BECAUSE CALIBRATION IS NOT SET")
                sleep(5)
                continue

            self.model.point()

            self.value += 1
            sleep(0.05)
        print("Exiting thread")

    def set_calibration(self, value: int) -> None:
        """ Sets the calibration value.
        """
        self.value = value
