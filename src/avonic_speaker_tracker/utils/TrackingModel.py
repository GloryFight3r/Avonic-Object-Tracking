from abc import ABC, abstractmethod
import numpy as np

class TrackingModel(ABC):
    @abstractmethod
    def point(self) -> np.ndarray:
        pass

    def set_speak_delay(self, speak_delay: int) -> None:
        pass
