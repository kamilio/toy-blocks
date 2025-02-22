from time import time
import machine

class AutoShutdown:
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = time()

    def maybe_deepsleep(self):
        if time() - self.start_time >= self.timeout:
            machine.deepsleep()