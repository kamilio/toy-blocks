from machine import Pin

class Led:
    def __init__(self, pin, active_low=False):
        self.led = Pin(pin, Pin.OUT)
        self.active_low = active_low
        self.off()

    def _set_value(self, value):
        logical_value = 1 if value else 0
        pin_value = not logical_value if self.active_low else logical_value
        self.led.value(pin_value)

    def on(self):
        self._set_value(1)

    def off(self):
        self._set_value(0)

    def toggle(self):
        current = self.led.value()
        self._set_value(not current)