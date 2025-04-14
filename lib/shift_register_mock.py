import pytest


class MockShiftRegister:
    def __init__(self):
        self.state = bytearray([0xFF])  # Initialize with 0xFF like the real implementation
        self.pins = {}
        self._in_batch = False

    def begin_batch(self):
        self._in_batch = True

    def end_batch(self):
        self._in_batch = False

    def set_pin(self, position, value):
        if not 0 <= position < 8:
            raise ValueError('Position must be between 0 and 7')
        if value:
            self.state[0] |= 1 << position
        else:
            self.state[0] &= ~(1 << position)
        self.pins[position] = value


class ShiftRegisterLed:
    def __init__(
        self, shift_register, position, active_low=True
    ):  # Default to active_low=True like real implementation
        self.shift_register = shift_register
        self.position = position
        self.active_low = active_low
        self.off()

    def value(self, val=None):
        if val is not None:
            self._set_value(val)
        return self.shift_register.pins.get(self.position, 0)

    def on(self):
        self._set_value(True)

    def off(self):
        self._set_value(False)

    def toggle(self):
        current = self.value()
        self._set_value(not current)

    def _set_value(self, value):
        actual_value = not value if self.active_low else value
        self.shift_register.set_pin(self.position, actual_value)


@pytest.fixture
def mock_shift_register():
    return MockShiftRegister()
