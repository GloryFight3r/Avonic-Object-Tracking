from time import sleep
from threading import Thread
from multiprocessing import Value
from ctypes import c_int
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI
from avonic_speaker_tracker.utils.TrackingModel import TrackingModel

class UpdateThread(Thread):

    def __init__(self, event: Value,
                 cam_api: CameraAPI, mic_api: MicrophoneAPI, model_index: Value, all_models: list[TrackingModel],
                 filepath: str = ""):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super().__init__()
        self.event: c_int = event

        self.cam_api: CameraAPI = cam_api
        self.mic_api: MicrophoneAPI = mic_api
        self.model_index = model_index.value
        self.all_models = all_models
        self.model_in_use = None
        self.value: int = 0
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
        prev_dir = [0.0, 0.0]
        speak_delay = 0


        print(self.model_index, self.all_models)

        self.model_in_use = self.all_models[self.model_index]
        self.model_in_use.reload()

        while self.event.value != 0:
            print("RUNNING UPDATE THREAD")

            if self.mic_api.is_speaking():
                speak_delay = 0
            else:
                speak_delay = speak_delay + 1
            #self.model_in_use.set_speak_delay(speak_delay)
            direct = self.model_in_use.point(self.cam_api, self.mic_api)

            print(direct)

            self.value += 1
            sleep(2)
        print("Exiting thread")
