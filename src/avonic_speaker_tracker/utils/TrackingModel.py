from abc import ABC, abstractmethod
import numpy as np
from avonic_camera_api.camera_control_api import CameraAPI
from microphone_api.microphone_control_api import MicrophoneAPI

class TrackingModel(ABC):
    @abstractmethod
    def point(self) -> np.ndarray:
        pass

    def set_speak_delay(self, speak_delay: int) -> None:
        pass
