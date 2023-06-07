from time import sleep
from threading import Thread
from ctypes import c_int
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel
from avonic_speaker_tracker.audio_model.calibration import Calibration
from avonic_speaker_tracker.preset_model.PresetModel import PresetModel

class UpdateThread(Thread):

    def __init__(self, event: c_int,
        cam_api: CameraAPI, mic_api: MicrophoneAPI, model):
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
        prev_dir = [0.0, 0.0]
        speak_delay: int = 0
        while self.event.value != 0:
            if self.value is None:
                print("STOPPED BECAUSE CALIBRATION IS NOT SET")
                sleep(5)
                continue

            if isinstance(self.model, PresetModel) and len(self.model.preset_locations.get_preset_list()) == 0:
                print("No locations preset")
            if self.mic_api.is_speaking():
                speak_delay = 0
                if isinstance(self.model, PresetModel):
                    prev_dir = self.model.point(self.cam_api, self.mic_api)
                else:
                    prev_dir = self.model.point()
            else:
                speak_delay = speak_delay + 1
            self.model.set_speak_delay(speak_delay)

            self.value += 1
            sleep(0.05)
        print("Exiting thread")

    def set_calibration(self, value: int) -> None:
        """ Sets the calibration value.
        """
        self.value = value
