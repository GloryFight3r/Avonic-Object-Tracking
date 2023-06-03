from time import sleep
from threading import Thread
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel
from avonic_speaker_tracker.audio_model.calibration import Calibration
from avonic_speaker_tracker.preset_model.PresetModel import PresetModel

class UpdateThread(Thread):
    loop = None

    def __init__(self, event,
        cam_api: CameraAPI, mic_api: MicrophoneAPI, preset_or_tracking):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super().__init__()
        self.event = event
        self.value = None
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.preset_or_tracking = preset_or_tracking.value
        self.model_in_use = None

    def run(self):
        """ Actual body of the thread.
        Continuously calls point method of the supplied model, to point the camera.
        """
        if self.preset_or_tracking == 0:
            self.model_in_use = AudioModel(filename="calibration.json")
        else:
            self.model_in_use = PresetModel(filename="presets.json")

        while self.event.value != 0:
            print("RUNNING")
            if self.value is None:
                print("STOPPED BECAUSE CALIBRATION IS NOT SET")
                sleep(5)
                continue
            print(self.model_in_use.point(self.cam_api, self.mic_api))

            self.value += 1
            sleep(0.3)
        print("Exiting thread")

    def set_calibration(self, value):
        """ Sets the calibration value.
        """
        self.value = value
