import sys
from unittest.mock import MagicMock

class MockPin:
    IN = 1
    OUT = 2
    PULL_UP = 3
    PULL_DOWN = 4
    
    def __init__(self, pin, mode=-1, pull=-1):
        self.pin = pin
        self.mode = mode
        self._value = 0

    def value(self, val=None):
        if val is not None:
            self._value = val
        return self._value


mock_machine = MagicMock()
mock_machine.Pin = MockPin
sys.modules['machine'] = mock_machine