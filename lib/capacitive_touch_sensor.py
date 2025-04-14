"""
Capacitive Touch Sensor Module

This module provides a class for interfacing with capacitive touch sensors (like TTP223)
on ESP32 microcontrollers. It handles the specific behavior of these sensors,
including proper debouncing and event callbacks.

Typical wiring:
- VCC: Connect to 3.3V
- GND: Connect to ground
- SIG/OUT: Connect to a GPIO pin (this is the pin you specify in the constructor)

Sensor Behavior:
- The sensor outputs LOW (0) when not touched
- The sensor outputs HIGH (1) when touched
- Some modules may have a jumper to change between toggle and momentary modes
"""

import time

import uasyncio
from logger import Logger
from machine import Pin


class CapacitiveTouchSensor:
    """
    A class for controlling capacitive touch sensors like TTP223.

    This class properly handles the touch sensor behavior:
    1. Provides debouncing to avoid false triggers
    2. Handles momentary touch mode (sensor outputs HIGH when touched)
    3. Allows registering callbacks for touch events
    """

    def __init__(self, pin, debounce_ms=50, active_high=True, pull_down=True, debug=False):
        """
        Initialize a capacitive touch sensor.

        Args:
            pin: The GPIO pin number connected to the sensor's SIG/OUT pin
            debounce_ms: Debounce time in milliseconds to avoid false triggers
            active_high: True if sensor outputs HIGH when touched (default behavior)
            pull_down: Whether to enable pull-down resistor on the pin
            debug: Enable debug logging
        """
        # Set up the pin with appropriate pull resistor
        if pull_down:
            self.pin = Pin(pin, Pin.IN, Pin.PULL_DOWN)
        else:
            self.pin = Pin(pin, Pin.IN)

        self.pin_num = pin
        self.active_high = active_high
        self.debounce_time = debounce_ms / 1000  # Convert to seconds

        # State tracking
        self.touched = False
        self.last_touch_time = 0
        self.last_state_change = 0
        self._running = False

        # Callbacks
        self._on_touch = None
        self._on_release = None
        self._on_toggle = None

        # Logger for debugging
        self.logger = Logger(prefix=f'CapacitiveTouchSensor(pin={pin})', debug=debug)
        self.logger.info('Initialized')

    def is_touched(self):
        """
        Check if the sensor is currently being touched.

        Returns:
            bool: True if touched, False otherwise
        """
        pin_value = self.pin.value()
        if self.active_high:
            return bool(pin_value)  # HIGH (1) means touched
        else:
            return not bool(pin_value)  # LOW (0) means touched

    def on_touch(self, callback):
        """
        Register a callback for when the sensor is touched.

        Args:
            callback: Function to call when sensor is touched
        """
        self._on_touch = callback

    def on_release(self, callback):
        """
        Register a callback for when the sensor is released.

        Args:
            callback: Function to call when sensor is released
        """
        self._on_release = callback

    def on_toggle(self, callback):
        """
        Register a callback for touch toggle (either touch or release).

        Args:
            callback: Function to call when sensor state changes
        """
        self._on_toggle = callback

    async def _run_callback(self, callback):
        """
        Run a callback asynchronously if it exists.

        Args:
            callback: The callback function to run
        """
        if callback is not None:
            try:
                # Try to create a task from the callback result
                # This assumes callback() returns a coroutine
                task = uasyncio.create_task(callback())
                await task
            except Exception as e:
                self.logger.info(f'Error in callback: {e}')

    async def monitor(self):
        """
        Start monitoring the touch sensor for state changes.
        This is an asynchronous function that should be run in an event loop.
        """
        self.logger.info('Starting touch sensor monitoring')
        self._running = True
        last_touched = None

        # For stability tracking
        stable_count = 0
        required_stability = 3  # Require 3 consistent readings for a state change
        current_reading = None

        while self._running:
            try:
                # Read the current state
                is_touched_now = self.is_touched()

                # For initial state
                if last_touched is None:
                    last_touched = is_touched_now
                    self.touched = is_touched_now
                    current_reading = is_touched_now
                    continue

                # Stability check to reduce noise/false triggers
                if is_touched_now == current_reading:
                    # Same reading, increment stability counter
                    stable_count += 1
                else:
                    # Different reading, reset counter and update current reading
                    stable_count = 0
                    current_reading = is_touched_now

                # Only process state change if we have stable readings
                if stable_count >= required_stability and current_reading != last_touched:
                    # State has changed and is stable
                    now = time.time()
                    time_since_last_change = now - self.last_state_change

                    # Only process if debounce time has passed
                    if time_since_last_change >= self.debounce_time:
                        # Update state tracking
                        self.touched = current_reading
                        last_touched = current_reading
                        self.last_state_change = now

                        # Log state change
                        state_str = 'TOUCHED' if current_reading else 'RELEASED'
                        self.logger.info(f'Touch state changed: {state_str}')

                        # Run appropriate callbacks
                        if current_reading:  # Touch event
                            self.last_touch_time = now
                            await self._run_callback(self._on_touch)
                        else:  # Release event
                            await self._run_callback(self._on_release)

                        # Always run toggle callback for any state change
                        await self._run_callback(self._on_toggle)

            except Exception as e:
                self.logger.info(f'Error in monitor: {e}')

            # Small sleep to avoid hogging the CPU
            await uasyncio.sleep(0.01)  # 10ms polling interval

    def stop(self):
        """Stop the touch sensor monitoring."""
        self._running = False
        self.logger.info('Stopped touch sensor monitoring')

    @staticmethod
    async def test_pin(pin, duration=5):
        """
        Test a pin to see if a capacitive touch sensor is connected and functional.

        Args:
            pin: The GPIO pin to test
            duration: How long to run the test in seconds

        Returns:
            dict: Test results including detected state changes
        """
        print(f'Testing pin {pin} for capacitive touch sensor...')

        # Try different pin configurations
        configs = [
            {'name': 'PULL_DOWN', 'pull': Pin.PULL_DOWN},
            {'name': 'PULL_UP', 'pull': Pin.PULL_UP},
            {'name': 'No Pull', 'pull': None},
        ]

        results = {}

        for config in configs:
            try:
                if config['pull'] is not None:
                    pin_obj = Pin(pin, Pin.IN, config['pull'])
                else:
                    pin_obj = Pin(pin, Pin.IN)

                print(f"Testing with {config['name']}...")

                # Monitor for state changes
                changes = 0
                initial_value = pin_obj.value()
                last_value = initial_value

                start_time = time.time()
                while time.time() - start_time < duration:
                    current_value = pin_obj.value()
                    if current_value != last_value:
                        changes += 1
                        print(f'  Value changed: {last_value} -> {current_value}')
                        last_value = current_value

                    await uasyncio.sleep(0.01)

                results[config['name']] = {
                    'initial_value': initial_value,
                    'final_value': last_value,
                    'changes': changes,
                }

                print(f'  Completed. Initial value: {initial_value}, Changes: {changes}')

            except Exception as e:
                print(f"Error testing config {config['name']}: {e}")
                results[config['name']] = {'error': str(e)}

        print('Test complete.')
        return results
