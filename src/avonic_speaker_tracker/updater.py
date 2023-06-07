from time import sleep
from threading import Thread
from multiprocessing import Value
from avonic_camera_api.camera_control_api import CameraAPI
from avonic_speaker_tracker.object_tracker_model.ObjectTrackingModel import HybridTracker
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel
from avonic_speaker_tracker.audio_model.AudioModel import AudioModel
from avonic_speaker_tracker.preset_model.PresetModel import PresetModel

class UpdateThread(Thread):
    event: Value = None
    value: int = None  
    cam_api: CameraAPI = None    
    mic_api: MicrophoneAPI = None    
    model_index: int = None    
    model_in_use: TrackingModel = None
    all_models: list[TrackingModel] = None

    def __init__(self, event: Value,
                 cam_api: CameraAPI, mic_api: MicrophoneAPI, model_index: Value, all_models: list[TrackingModel]):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super().__init__()
        self.event = event
        self.cam_api = cam_api
        self.mic_api = mic_api
        self.model_index = model_index.value
        self.all_models = all_models
        self.model_in_use = None

    def run(self):
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
        speak_delay = 0

        self.model_in_use = self.all_models[self.model_index]
        self.model_in_use.reload()

        print(self.model_index)

        while self.event.value != 0:
            print("RUNNING")

            if self.mic_api.is_speaking():
                speak_delay = 0 
            else:
                speak_delay = speak_delay + 1 
            self.model_in_use.set_speak_delay(speak_delay)
            direct = self.model_in_use.point(self.cam_api, self.mic_api)

            print(direct)

            sleep(0.05)
        print("Exiting thread")
