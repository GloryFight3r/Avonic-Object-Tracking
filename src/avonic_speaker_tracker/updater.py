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
                 cam_api: CameraAPI, mic_api: MicrophoneAPI, model):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super().__init__()
        self.event = event
        self.value = None
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.model = model
        #self.model_in_use = None

    def run(self):
        """ Actual body of the thread.
        Continuously calls point method of the supplied model, to point the camera.
        """
        prev_dir = [0.0, 0.0]
        speak_delay = 0
        #if self.preset_or_tracking == ModelCode.PRESET:
        #    self.model_in_use = AudioModel(filename="calibration.json")
        #else:
        #    self.model_in_use = PresetModel(filename="presets.json")

        print("THREAD EVENT")
        print(self.event.value)
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

            #print(direct)
            self.value += 1
            sleep(0.05)
        print("Exiting thread")

    def set_calibration(self, value):
        """ Sets the calibration value.
        """
        self.value = value
