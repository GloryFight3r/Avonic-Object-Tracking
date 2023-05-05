class Microphone:
    # height in meters
    height = None

    def __init__(self):
        self.height = 0

    def set_height(self, height: float):
        assert height >= 0.0
        self.height = height
