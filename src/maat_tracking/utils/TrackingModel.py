from abc import ABC, abstractmethod
import numpy as np

class TrackingModel(ABC):
    prev_dir: np.ndarray = None
    @abstractmethod
    def point(self) -> np.ndarray:
        pass

    def set_speak_delay(self, speak_delay: int) -> None:
        pass

    @abstractmethod
    def sleep(self):
        pass
