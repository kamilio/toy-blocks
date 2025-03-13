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
        self._prev_state = 0  # Start with LED off
        self.off()  # Ensure LED starts in known state

    def _set_value(self, value):
        # Convert input to 1 or 0
        logical_value = 1 if value else 0
        # For active_low, invert the pin value
        pin_value = not logical_value if self.active_low else logical_value
        
        self.led.value(pin_value)

    def _get_value(self):
        pin_value = self.led.value()
        # For active_low, invert the logical value
        if self.active_low:
            return 1 if pin_value == 0 else 0
        return pin_value
    
    async def blink(self, count=1, interval=0.5):
        self._prev_state = self._get_value()
        
        for i in range(count):
            self._set_value(1)  # ON
            await uasyncio.sleep(interval)
            self._set_value(0)  # OFF
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
    
    def on(self):
        self._set_value(1)
    
    def off(self):
        self._set_value(0)