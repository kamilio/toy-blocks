from time import time
import machine
import uasyncio

class AutoShutdown:
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = time()
        self._running = False

    def reset_timer(self):
        self.start_time = time()

    async def maybe_deepsleep(self):
        if time() - self.start_time >= self.timeout:
            machine.deepsleep()

    async def monitor(self):
        self._running = True
        while self._running:
            await self.maybe_deepsleep()
            await uasyncio.sleep(10)

    def stop(self):
        self._running = False