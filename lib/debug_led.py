from machine import Pin
import uasyncio
from board_config import BoardConfig

class DebugLed:
    def __init__(self, pin=None, active_low=None):
        board = BoardConfig()
        pin = pin if pin is not None else board.LED_PIN
        active_low = active_low if active_low is not None else board.is_builtin_led_active_low()
        self.led = Pin(pin, Pin.OUT)
        self.active_low = active_low
        self._blink_forever = False
        self._prev_state = 0

    def _set_value(self, value):
        self.led.value(0 if value else 1) if self.active_low else self.led.value(value)

    def _get_value(self):
        value = self.led.value()
        return not value if self.active_low else value
    
    async def blink(self, count=1, interval=0.5):
        self._prev_state = self._get_value()
        for _ in range(count):
            self._set_value(1)
            await uasyncio.sleep(interval)
            self._set_value(0)
            await uasyncio.sleep(interval)
        self._set_value(self._prev_state)
    
    async def blink_forever(self, interval=0.5):
        self._blink_forever = True
        self._prev_state = self._get_value()
        while self._blink_forever:
            self._set_value(1)
            await uasyncio.sleep(interval)
            self._set_value(0)
            await uasyncio.sleep(interval)
        self._set_value(self._prev_state)
    
    def stop_blinking(self):
        self._blink_forever = False
        # LED state will be restored in blink_forever when loop ends
        pass
    
    def on(self):
        self._set_value(1)
    
    def off(self):
        self._set_value(0)