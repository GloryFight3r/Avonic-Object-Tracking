class MicrophoneAPI:
    def __init__(self, microphone):
        self.microphone = microphone

    def set_height(self, height: float):
        self.microphone.set_height(height)
