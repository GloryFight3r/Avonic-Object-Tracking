from abc import ABC, abstractmethod
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI

class TrackingModel(ABC):
    prev_dir: np.ndarray = None
    @abstractmethod
    def point(self, cam_api: CameraAPI, mic_api: MicrophoneAPI):
        pass
