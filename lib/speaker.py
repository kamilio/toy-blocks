from machine import Pin, PWM
from time import sleep
from enum import IntEnum

class Note(IntEnum):
    REST = 0
    C4 = 262
    CS4 = 277
    D4 = 294
    DS4 = 311
    E4 = 330
    F4 = 349
    FS4 = 370
    G4 = 392
    GS4 = 415
    A4 = 440
    AS4 = 466
    B4 = 494
    C5 = 523

class Duration(IntEnum):
    WHOLE = 1000
    HALF = 500
    QUARTER = 250
    EIGHTH = 125
    SIXTEENTH = 63
    THIRTYSECOND = 31

class PWMWrapper:
    def __init__(self, pin: Pin, freq: int = 440):
        self.pin = pin
        self.freq = freq
        self.duty_u16 = 0

class Speaker:
    def __init__(self, pin1: int, pin2: int, freq: int = 440) -> None:
        self.pwm1 = PWMWrapper(Pin(pin1, Pin.OUT), freq)
        self.pwm2 = PWMWrapper(Pin(pin2, Pin.OUT), freq)
    
    def _turn_on(self) -> None:
        self.pwm1.duty_u16 = 32768  # 50% duty cycle
        self.pwm2.duty_u16 = 32768
    
    def _turn_off(self) -> None:
        self.pwm1.duty_u16 = 0
        self.pwm2.duty_u16 = 0
    
    def beep(self, count: int = 1, duration_ms: int = 100, interval_ms: int = 100) -> None:
        for _ in range(count):
            self._turn_on()
            sleep(duration_ms / 1000)  # Convert ms to seconds
            self._turn_off()
            if count > 1:
                sleep(interval_ms / 1000)  # Convert ms to seconds
    
    def play_note(self, note: Note, duration: Duration) -> None:
        if note == Note.REST:
            self._turn_off()
        else:
            self.pwm1.freq = note
            self.pwm2.freq = note
            self._turn_on()
        sleep(duration / 1000)
        self._turn_off()
    
    def play_song(self, song: list[tuple[Note, Duration]]) -> None:
        for note, duration in song:
            self.play_note(note, duration)