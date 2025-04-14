import uasyncio as asyncio
from machine import PWM, Pin

from lib.logger import Logger


class AudioAmplifier:
    MAX98357A = 'MAX98357A'
    PAM8403 = 'PAM8403'

    def __init__(self, data_pin, amp_type=PAM8403, shutdown_pin=None, sample_rate=44100, volume=50):
        self.amp_type = amp_type
        self.sample_rate = sample_rate
        self._volume = volume
        self.logger = Logger('AudioAmplifier', debug=False)

        self.data_pin = Pin(data_pin, Pin.OUT)
        self.pwm = PWM(self.data_pin)
        self.pwm.freq(sample_rate)
        self.pwm.duty_u16(0)

        self.shutdown_pin = None
        if shutdown_pin is not None:
            self.shutdown_pin = Pin(shutdown_pin, Pin.OUT)
            if amp_type == self.MAX98357A:
                self.shutdown_pin.value(1)
            else:
                self.shutdown_pin.value(0)

        self._monitor_task = None
        self._running = False
        self._callbacks = {
            'status_change': None,
            'playback_started': None,
            'playback_completed': None,
        }

        self._playing = False
        self._playback_task = None
        self._current_sample_idx = 0
        self._current_audio_data = None
        self._timer = None

        self.logger.info(f'Initialized {amp_type} amplifier on pin {data_pin}')

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        if 0 <= value <= 100:
            self._volume = value
            self.logger.info(f'Volume set to {value}%')
        else:
            self.logger.error(f'Invalid volume level: {value}')

    def enable(self):
        if self.shutdown_pin is not None:
            if self.amp_type == self.MAX98357A:
                # MAX98357A is enabled when SD pin is high
                self.shutdown_pin.value(1)
            else:
                # PAM8403 typically uses active-low shutdown
                self.shutdown_pin.value(1)
            self.logger.info('Amplifier enabled')

    def disable(self):
        if self.shutdown_pin is not None:
            if self.amp_type == self.MAX98357A:
                # MAX98357A is disabled when SD pin is low
                self.shutdown_pin.value(0)
            else:
                # PAM8403 typically uses active-low shutdown
                self.shutdown_pin.value(0)
            self.logger.info('Amplifier disabled')

        # Make sure PWM is off
        self.pwm.duty_u16(0)

    async def play_wav(self, sd_reader, filename):
        if self._playing:
            await self.stop_playback()

        self.logger.info(f'Loading WAV file: {filename}')
        result = await sd_reader.read_wav(filename)
        if not result:
            self.logger.error(f'Failed to read WAV file: {filename}')
            return False

        sample_rate, audio_data = result
        self.logger.info(f'WAV loaded: {len(audio_data)} bytes, {sample_rate}Hz')

        # Update sample rate if different
        if sample_rate != self.sample_rate:
            self.sample_rate = sample_rate
            self.pwm.freq(sample_rate)

        # Start playback
        self._current_audio_data = audio_data
        self._current_sample_idx = 0
        self._playing = True

        # Enable amplifier
        self.enable()

        # Start playback task
        self._playback_task = asyncio.create_task(self._playback_loop())
        return True

    async def stop_playback(self):
        if not self._playing:
            return

        self._playing = False
        if self._playback_task:
            # Wait for playback task to complete
            await self._playback_task
            self._playback_task = None

        # Clear playback state
        self._current_audio_data = None
        self._current_sample_idx = 0

        # Disable output
        self.pwm.duty_u16(0)
        self.logger.info('Playback stopped')

    async def _playback_loop(self):
        if not self._current_audio_data:
            return

        chunk_size = min(1024, len(self._current_audio_data))

        while self._playing and self._current_sample_idx < len(self._current_audio_data):
            end_idx = min(self._current_sample_idx + chunk_size, len(self._current_audio_data))
            chunk = self._current_audio_data[self._current_sample_idx : end_idx]

            if self.amp_type == self.MAX98357A:
                for sample in chunk:
                    duty = int((sample / 255) * 65535 * (self._volume / 100))
                    self.pwm.duty_u16(duty)
                    await asyncio.sleep(1 / self.sample_rate)
            else:
                for sample in chunk:
                    duty = int((sample / 255) * 65535 * (self._volume / 100))
                    self.pwm.duty_u16(duty)
                    await asyncio.sleep(1 / self.sample_rate)

            self._current_sample_idx = end_idx
            await asyncio.sleep(0)

        if self._current_sample_idx >= len(self._current_audio_data):
            self.logger.info('Playback completed')
            self._playing = False
            self.pwm.duty_u16(0)

    def on_status_change(self, callback):
        self._callbacks['status_change'] = callback

    def on_playback_started(self, callback):
        self._callbacks['playback_started'] = callback

    def on_playback_completed(self, callback):
        self._callbacks['playback_completed'] = callback

    async def start_monitoring(self, callback):
        if self._running:
            return

        # Register the callback for status changes
        self._callbacks['status_change'] = callback

        # Start monitoring
        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor())

        # Give the task a chance to start
        await asyncio.sleep(0)
        self.logger.info('Started monitoring')

    async def monitor(self):
        if self._running:
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor())

        # Give the task a chance to start
        await asyncio.sleep(0)
        self.logger.info('Started monitoring')

    def stop(self):
        self._running = False
        self.logger.info('Monitoring stopped')

    async def _run_callback(self, callback_type, data=None):
        callback = self._callbacks.get(callback_type)
        if callback:
            await asyncio.create_task(callback(data))

    async def _monitor(self):
        was_playing = self._playing

        while self._running:
            status = {
                'playing': self._playing,
                'volume': self._volume,
                'type': self.amp_type,
                'sample_rate': self.sample_rate,
            }

            if not was_playing and self._playing:
                await self._run_callback('playback_started', status)

            if was_playing and not self._playing and self._current_sample_idx > 0:
                playback_completed = self._current_audio_data and self._current_sample_idx >= len(
                    self._current_audio_data
                )
                if playback_completed:
                    await self._run_callback('playback_completed', status)

            if self._playing and self._current_audio_data:
                progress = 0
                if len(self._current_audio_data) > 0:
                    progress = (self._current_sample_idx / len(self._current_audio_data)) * 100
                status['progress'] = progress

            await self._run_callback('status_change', status)
            was_playing = self._playing

            await asyncio.sleep(0.1)
