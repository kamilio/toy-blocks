from machine import Pin
import uasyncio
import time
from pins import BOOT_BUTTON

class BoardButton:
    def __init__(self, callback=None):
        self.boot_button = Pin(BOOT_BUTTON, Pin.IN, Pin.PULL_UP)
        self._running = False
        self.on_press(callback) if callback else None
        self._debounce_delay = 0.05
        self._last_press_time = 0
        self._was_pressed = False
        
    def is_boot_pressed(self):
        return not self.boot_button.value()
    
    def on_press(self, callback):
        self._callback = callback
        
    async def _handle_press(self):
        current_time = time.time()
        if current_time - self._last_press_time < self._debounce_delay:
             return
            
        self._last_press_time = time.time()
        
        if self._callback:
            await uasyncio.create_task(self._callback())
    async def _check_once(self):
        is_pressed = self.is_boot_pressed()
            
        if is_pressed and not self._was_pressed:
            await self._handle_press()
        
        self._was_pressed = is_pressed
    
    async def monitor_buttons(self):
        self._running = True
        while self._running:
            await self._check_once()
            await uasyncio.sleep(0.1)
            
    def stop(self):
        self._running = False