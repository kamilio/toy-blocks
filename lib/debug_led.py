from machine import Pin
import uasyncio
from pins import BUILTIN_LED

class DebugLed:
    def __init__(self, pin=BUILTIN_LED):
        self.led = Pin(pin, Pin.OUT)
        self._blink_forever = False
    
    async def blink(self, count=1, interval=0.5):
        for _ in range(count):
            self.led.value(1)
            await uasyncio.sleep(interval)
            self.led.value(0)
            if _ < count - 1:
                await uasyncio.sleep(interval)
    
    async def blink_forever(self, interval=0.5):
        self._blink_forever = True
        while self._blink_forever:
            self.led.value(1)
            await uasyncio.sleep(interval)
            self.led.value(0)
            await uasyncio.sleep(interval)
    
    def stop_blinking(self):
        self._blink_forever = False
        self.led.value(0)
    
    def on(self):
        self.led.value(1)
    
    def off(self):
        self.led.value(0)