from machine import Pin
import uasyncio
import time
from logger import Logger

class Button:
    def __init__(self, pin: int, pin_mode=Pin.IN, pull=Pin.PULL_UP, debug=True):
        self.pin = Pin(pin, pin_mode, pull)
        self._running = False
        self.logger = Logger(prefix=f"Button(pin={pin})", debug=debug)
        
        # Timing configuration - extreme priority for double-click detection
        self._double_click_timeout = 0.7  # 700ms maximum time between clicks for double-click
        self._long_press_time = 1.2      # Increased to avoid false positives
        
        # Simplified state tracking focused on reliability
        self._press_start_time = None    # When button was pressed (for long press)
        self._click_times = []           # Times of recent clicks
        self._was_pressed = False        # Previous button state
        
        # Callbacks
        self._callbacks = {'single': None, 'double': None, 'triple': None, 'long': None, 'down': None, 'up': None}
        
        self.logger.info("Initialized with SIMPLIFIED double-click detection")
        
    def is_pressed(self):
        # Pull-up means 0 is pressed, 1 is released
        return not bool(self.pin.value())
    
    def on_press(self, callback):
        self._callbacks['single'] = callback
        self.logger.info("Registered single press callback")
        
    def on_double_press(self, callback):
        self._callbacks['double'] = callback
        self.logger.info("Registered double press callback")
        
    def on_triple_press(self, callback):
        self._callbacks['triple'] = callback
        self.logger.info("Registered triple press callback")
        
    def on_long_press(self, callback):
        self._callbacks['long'] = callback
        self.logger.info("Registered long press callback")
        
    def on_button_down(self, callback):
        self._callbacks['down'] = callback
        self.logger.info("Registered button down callback")
        
    def on_button_up(self, callback):
        self._callbacks['up'] = callback
        self.logger.info("Registered button up callback")
    
    async def _run_callback(self, callback_type):
        """Run a callback by name with error handling"""
        callback = self._callbacks[callback_type]
        if callback is None:
            return
            
        try:
            result = callback()
            if result is not None:
                try:
                    await result  # type: ignore
                except TypeError:
                    pass  # Not awaitable
        except Exception as e:
            self.logger.info(f"Error executing {callback_type} callback: {str(e)}")
    
    def _clean_old_clicks(self, now=None):
        """Remove clicks older than double-click timeout"""
        if now is None:
            now = time.time()
        self._click_times = [t for t in self._click_times if now - t < self._double_click_timeout]
    
    async def _check_once(self):
        """Simplified button handling focused on double-click detection"""
        now = time.time()
        is_pressed = self.is_pressed()
        
        # Clean up old clicks
        self._clean_old_clicks(now)
        
        # Button press event (transition from not pressed to pressed)
        if is_pressed and not self._was_pressed:
            self.logger.info("Button DOWN")
            self._press_start_time = now
            
            # Execute down callback
            if self._callbacks['down']:
                await self._run_callback('down')
        
        # Button long press check
        elif is_pressed and self._was_pressed and self._press_start_time is not None:
            # Check for long press
            if now - self._press_start_time >= self._long_press_time and self._callbacks['long']:
                self.logger.info("Long press detected")
                await self._run_callback('long')
                self._press_start_time = None  # Reset to avoid triggering again
        
        # Button release event (transition from pressed to not pressed)
        elif not is_pressed and self._was_pressed:
            self.logger.info("Button UP")
            
            # Register click time
            if self._press_start_time is not None:
                self._click_times.append(now)
                self.logger.info(f"Click registered, total recent clicks: {len(self._click_times)}")
                self._press_start_time = None  # Reset press start time
            
            # Check for double/triple click
            if len(self._click_times) == 2 and self._callbacks['double']:
                self.logger.info("Double click detected!")
                await self._run_callback('double')
                self._click_times = []  # Clear after processing
            elif len(self._click_times) >= 3 and self._callbacks['triple']:
                self.logger.info("Triple click detected!")
                await self._run_callback('triple')
                self._click_times = []  # Clear after processing
            elif len(self._click_times) == 1 and self._callbacks['single'] and not self._callbacks['double']:
                # Only handle single click immediately if double clicks aren't supported
                self.logger.info("Single click with no double handler")
                await self._run_callback('single')
                self._click_times = []  # Clear after processing
            
            # Execute up callback
            if self._callbacks['up']:
                await self._run_callback('up')
        
        # Process single clicks after timeout if needed
        elif len(self._click_times) == 1 and now - self._click_times[0] >= self._double_click_timeout:
            # No second click within timeout - handle as single click
            if self._callbacks['single']:
                self.logger.info("Single click (timeout reached)")
                await self._run_callback('single')
            self._click_times = []  # Clear click times
        
        # Update button state
        self._was_pressed = is_pressed
    
    async def monitor(self):
        """Monitor button with ultra-fast sampling"""
        self.logger.info("Starting button monitor")
        self._running = True
        while self._running:
            try:
                await self._check_once()
                await uasyncio.sleep(0.001)  # 1ms ultra-fast sampling
            except Exception as e:
                self.logger.info(f"Error in monitor: {str(e)}")
                await uasyncio.sleep(0.1)  # Delay on error
            
    def stop(self):
        self.logger.info("Stopping button monitor")
        self._running = False
