from threading import Thread
import base64
import time
import cv2

class FootageThread(Thread):
    def __init__(self, camera_footage: cv2.VideoCapture, event):
        """ Constructor for the footage thread

        Args:
            event (): event that stops the thread
            camera_footage: object to read from camera footage
        """
        super().__init__()
        self.camera_footage = camera_footage
        self.success = None
        self.frame = None
        self.event = event
        self.ret = None
        self.buffer = None

    def run(self):
        """ Body of the thread that keeps receiving camera footage and loads it into the buffer """
        while not self.event.is_set():
            time.sleep(0.01)
            self.success, self.frame = self.camera_footage.read()  # read the camera frame
            if self.success:
                self.ret, self.buffer = cv2.imencode('.jpg', self.frame)
            else:
                break

    def get_frame(self):
        """ Returns the camera footage image decoded into ascii
        
        Returns:
            
        """
        data = base64.b64encode(self.buffer).decode('ascii')
        return data
