class MicrophoneAPI:
    def __init__(self, microphone):
        self.microphone = microphone

    def set_height(self, height: float):
        """
        Sets the height of the microphone.

            Parameters:
                height (float): the new height
        """
        self.microphone.set_height(height)
