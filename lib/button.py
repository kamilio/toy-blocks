import time

import uasyncio
from logger import Logger
from machine import Pin


class Button:
    def __init__(self, pin: int, pin_mode=Pin.IN, pull=Pin.PULL_UP, debug=True):
        try:
            self.pin = Pin(pin, pin_mode, pull)
        except ValueError as e:
            raise ValueError(f'Invalid pin number {pin}: {e!s}') from e

        self._running = False
        self.logger = Logger(prefix=f'Button(pin={pin})', debug=debug)
        self._callbacks = {'down': None, 'up': None, 'press': None}
        self._was_pressed = None
        self.was_pressed = False

    def is_pressed(self):
        return not bool(self.pin.value())

    def on_button_down(self, callback):
        self._callbacks['down'] = callback

    def on_button_up(self, callback):
        self._callbacks['up'] = callback

    def on_press(self, callback):
        self._callbacks['press'] = callback

    async def _run_callback(self, callback_type):
        callback = self._callbacks[callback_type]
        if callback:
            try:
                task = uasyncio.create_task(callback())
                await task
            except Exception as e:
                self.logger.info(f'Error executing {callback_type} callback: {e!s}')

    async def _check_once(self):
        is_pressed = self.is_pressed()

        if self._was_pressed is None:
            self._was_pressed = is_pressed
            return

        if is_pressed and not self._was_pressed:
            await self._run_callback('down')
            self._was_pressed = True
        elif not is_pressed and self._was_pressed:
            await self._run_callback('press')
            await self._run_callback('up')
            self._was_pressed = False
            self.was_pressed = True

    async def monitor(self):
        self._running = True
        while self._running:
            try:
                await self._check_once()
                await uasyncio.sleep(0.001)
            except Exception as e:
                self.logger.info(f'Error in monitor: {e!s}')
                await uasyncio.sleep(0.1)

    def stop(self):
        self._running = False

    def consume_was_pressed(self):
        """Returns True if the button was pressed since last check and resets the state"""
        was_pressed = self.was_pressed
        self.was_pressed = False
        return was_pressed


class DebouncedButton(Button):
    def __init__(self, pin: int, debounce_ms=20, **kwargs):
        super().__init__(pin, **kwargs)
        self._debounce_time = debounce_ms / 1000
        self._last_press = -self._debounce_time
        self._last_release = -self._debounce_time

    async def _check_once(self):
        now = time.time()
        is_pressed = self.is_pressed()

        if self._was_pressed is None:
            self._was_pressed = is_pressed
            return

        if is_pressed != self._was_pressed:
            if is_pressed and now - self._last_press >= self._debounce_time:
                await self._run_callback('down')
                self._was_pressed = True
                self._last_press = now
            elif not is_pressed and now - self._last_release >= self._debounce_time:
                await self._run_callback('press')
                await self._run_callback('up')
                self._was_pressed = False
                self._last_release = now
