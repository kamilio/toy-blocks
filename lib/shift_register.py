import time

from machine import Pin

from lib.led import Led
from lib.logger import Logger

# SN74HC595N
#       ┌───────┐
#   1 ──┤O      ├── 16
#   2 ──┤       ├── 15
#   3 ──┤       ├── 14
#   4 ──┤       ├── 13
#   5 ──┤       ├── 12
#   6 ──┤       ├── 11
#   7 ──┤       ├── 10
#   8 ──┤       ├── 9
#       └───────┘

#       ┌───────────────────┐
#   1 ──┤Q1 → LED 2         ├── 16 (VCC → 5V)
#   2 ──┤Q2 → LED 3         ├── 15 (Q0 → LED 1)
#   3 ──┤Q3 → LED 4         ├── 14 (DS → ESP32 GPIO 32 [ser])
#   4 ──┤Q4 → LED 5         ├── 13 (OE → GND)
#   5 ──┤Q5 → LED 6         ├── 12 (STCP → ESP32 GPIO 33 [rclk])
#   6 ──┤Q6 → LED 7         ├── 11 (SHCP → ESP32 GPIO 26 [srclk])
#   7 ──┤Q7 → LED 8         ├── 10 (MR → 5V)
#   8 ──┤GND → Ground       ├── 9  (Q7' → NC or next IC)
#       └───────────────────┘

# Wire color coding
# ser - DS (Data Serial) - Blue
# rclk - STCP (Storage Register Clock) - Green
# srclk - SHCP (Shift Register Clock) - Yellow


class ShiftRegister:
    def __init__(self, ser, rclk, srclk, registers=1, position=0, state=None):
        self.ser = ser  # Store original pin numbers
        self.rclk = rclk
        self.srclk = srclk
        self.ser_pin = Pin(ser, Pin.OUT)
        self.rclk_pin = Pin(rclk, Pin.OUT)
        self.srclk_pin = Pin(srclk, Pin.OUT)
        self.registers = registers
        self.position = position
        self.state = state if state is not None else bytearray([0] * registers)
        self.batch_mode = False

    def _pulse_clock(self, pin):
        pin.value(0)
        time.sleep(0.000001)  # 1 microsecond delay
        pin.value(1)
        time.sleep(0.000001)
        pin.value(0)

    def update(self):
        # Send data for all registers, starting with the last one
        for reg in range(self.registers - 1, -1, -1):
            state = self.state[reg]
            # Send each bit, MSB first
            for i in range(7, -1, -1):
                bit = (state >> i) & 1
                # We must use a deterministic approach to set the value
                # so the sr.history contains a predictable pattern
                # First always set to 0, then set to the actual bit value if needed
                self.ser_pin.value(0)
                if bit:
                    self.ser_pin.value(1)
                self._pulse_clock(self.srclk_pin)

        # Latch the data
        self._pulse_clock(self.rclk_pin)

    def set_pin(self, position, value):
        if not 0 <= position < 8:
            raise ValueError('Position must be between 0 and 7')

        # Use LSB ordering for internal state storage
        mask = 1 << position
        if value:
            self.state[self.position] |= mask
        else:
            self.state[self.position] &= ~mask

        # Only update the physical shift register if not in batch mode
        if not self.batch_mode:
            self.update()

    def begin_batch(self):
        """Enter batch mode - defer updates until end_batch is called"""
        self.batch_mode = True

    def end_batch(self):
        """Exit batch mode and apply all pending updates"""
        self.batch_mode = False
        self.update()

    def get_pin(self, position):
        if not 0 <= position < 8:
            raise ValueError('Position must be between 0 and 7')

        # Use LSB ordering for internal state
        mask = 1 << position
        return 1 if self.state[self.position] & mask else 0

    def clear(self):
        for i in range(self.registers):
            self.state[i] = 0x00
        self.update()

    def fill(self):
        for i in range(self.registers):
            self.state[i] = 0xFF
        self.update()

    def next(self):
        if self.position >= self.registers - 1:
            raise ValueError('No more registers in chain')
        return ShiftRegister(
            self.ser, self.rclk, self.srclk, self.registers, self.position + 1, self.state
        )

    def test_sequence(self):
        """Run a test sequence to verify shift register operation"""
        # First clear everything
        self.clear()
        # Then turn on each LED one by one
        for i in range(8):
            self.set_pin(i, True)
            # Wait a bit to see the LED
            import time

            time.sleep(0.5)
        # Then turn off each LED one by one
        for i in range(8):
            self.set_pin(i, False)
            import time

            time.sleep(0.5)
        # Finally do a blink pattern
        for _ in range(3):
            self.fill()
            import time

            time.sleep(0.5)
            self.clear()
            time.sleep(0.5)

    @property
    def q0(self):
        return (self, 0)

    @property
    def q1(self):
        return (self, 1)

    @property
    def q2(self):
        return (self, 2)

    @property
    def q3(self):
        return (self, 3)

    @property
    def q4(self):
        return (self, 4)

    @property
    def q5(self):
        return (self, 5)

    @property
    def q6(self):
        return (self, 6)

    @property
    def q7(self):
        return (self, 7)


class VirtualPin:
    def __init__(self, shift_register, position):
        self.shift_register = shift_register
        self.position = position

    def value(self, val=None):
        if val is not None:
            self.shift_register.set_pin(self.position, val)
            return None
        return self.shift_register.get_pin(self.position)


class ShiftRegisterLed(Led):
    def __init__(
        self, shift_register, position, active_low=True
    ):  # Default to active_low=True since we found LEDs are active low
        self._virtual_pin = VirtualPin(shift_register, position)
        self.logger = Logger(prefix=f'LED{position}', debug=False)
        self.logger.set_threshold(0.5)

        self.active_low = active_low  # Set this before super().__init__
        super().__init__(self._virtual_pin, active_low)

    @property
    def shift_register(self):
        return self._virtual_pin.shift_register

    @property
    def position(self):
        return self._virtual_pin.position

    def _set_value(self, value):
        self.logger.info(
            f"Setting to {'ON' if value else 'OFF'} (active {'low' if self.active_low else 'high'})"
        )
        pin_value = not value if self.active_low else value
        self._virtual_pin.value(pin_value)

    def toggle(self):
        # Simply read the current pin value and invert it
        # The _set_value method will handle the active_low conversion
        current = self._virtual_pin.value()
        self._set_value(not current)
