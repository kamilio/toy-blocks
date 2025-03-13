from machine import Pin, PWM
import uasyncio
from speaker_types import Note, Duration
from logger import Logger

class PWMWrapper:
    def __init__(self, pin, freq=440):
        self.pin = pin
        self.pwm = PWM(pin)
        self._freq = freq
        self._duty = 0
        self.pwm.freq(self._freq)

    @property
    def freq(self):
        return self._freq

    @freq.setter
    def freq(self, value):
        self._freq = int(value)
        self.pwm.freq(self._freq)

    @property
    def duty_u16(self):
        return self._duty
    
    @duty_u16.setter
    def duty_u16(self, value):
        self._duty = value
        self.pwm.duty_u16(value)

class Speaker:
    def __init__(self, pin: int, freq=440):
        self.pwm = PWMWrapper(Pin(pin, Pin.OUT), freq)
        self.logger = Logger("Speaker", debug=True)
    
    def _turn_on(self):
        self.pwm.duty_u16 = 32768  # 50% duty cycle
        self.logger.info("Speaker turned on")
    
    def _turn_off(self):
        self.pwm.duty_u16 = 0
        self.logger.info("Speaker turned off")
    
    async def beep(self, count=1, duration_ms=100, interval_ms=100):
        for i in range(count):
            self._turn_on()
            await uasyncio.sleep(duration_ms / 1000)  # Convert ms to seconds
            self._turn_off()
            if count > 1:
                await uasyncio.sleep(interval_ms / 1000)  # Convert ms to seconds
    
    async def play_note(self, note, duration):
        if not isinstance(note, Note):
            note = Note.from_int(note)
        if not isinstance(duration, Duration):
            duration = Duration.from_int(duration)

        if note == Note.REST:
            self._turn_off()
        else:
            self.pwm.freq = int(note)
            self._turn_on()
            
        await uasyncio.sleep(int(duration) / 1000)  # Convert ms to seconds
        self._turn_off()
    
    async def play_song(self, song):
        self.logger.info("Starting to play song")
        for note, duration in song:
            await self.play_note(note, duration)
            if note != Note.REST:
                await uasyncio.sleep(0.05)  # Small gap between notes