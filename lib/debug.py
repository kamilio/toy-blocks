from machine import Pin
import time
from pins import BUILTIN_LED

class Debug:
    def __init__(self):
        self.led = Pin(BUILTIN_LED, Pin.OUT)
        self._blink_forever = False
    
    def blink(self, count=1, interval=0.5):
        for _ in range(count):
            self.led.value(1)
            time.sleep(interval)
            self.led.value(0)
            if _ < count - 1:
                time.sleep(interval)
    
    def blink_forever(self, interval=0.5):
        self._blink_forever = True
        while self._blink_forever:
            self.led.value(1)
            time.sleep(interval)
            self.led.value(0)
            time.sleep(interval)
    
    def stop_blinking(self):
        self._blink_forever = False
        self.led.value(0)
    
    def on(self):
        self.led.value(1)
    
    def off(self):
        self.led.value(0)