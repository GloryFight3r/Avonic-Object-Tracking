from time import sleep
from threading import Thread
from multiprocessing import Value
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

        The model can be one of the below:
        - AudioModel aka continuous tracking based on microphone information.
        - PresetModel aka presets, which selects the camera direction
        from the limited pool of options, based on cosine similarity.
        - ObjectModel aka using object detection to figure out where to move
        the camera.
        """
        prev_dir = [0.0, 0.0]
        speak_delay: int = 0
        
        while self.event.value != 0:
            self.model.point()
            sleep(0.3)

        print("Exiting thread")
