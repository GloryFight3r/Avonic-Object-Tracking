from time import sleep
from threading import Thread


class CustomThread(Thread):
    # Custom thread class use a skeleton
    def __init__(self, event):
        """ Class constructor

        Args:
            event - event from threading module, that acts as a flag/lock of the thread
        """
        super(CustomThread, self).__init__()
        self.event = event
        self.value = None
 
    def run(self):
        """ Actual body of the thread.
        Method should start with self.event.wait() to make sure that on
        start of the thread with false flag, body of the while-loop is not executed.
        """
        while not self.event.is_set():
            if self.value is None:
                print("STOPPED BECAUSE CALIBRATION IS NOT SET")
                sleep(5)
                continue
            print('Worker thread running...')
            self.value += 1
            sleep(1)
        print('Worker closing down')

    def set_calibration(self, value):
        self.value = value