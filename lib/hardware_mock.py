from unittest.mock import MagicMock
from pin_mock import MockPin

class MockRTC:
    def __init__(self):
        self._memory = bytearray([0] * 5)
        self._datetime = (2024, 1, 1, 1, 0, 0, 0, 0)
    
    def memory(self, value=None):
        if value is not None:
            self._memory = value
            return None
        return self._memory
    
    def datetime(self, datetime=None):
        if datetime is not None:
            self._datetime = datetime
            return None
        return self._datetime

# Mock machine module
mock_machine = MagicMock()
mock_machine.RTC = MockRTC
mock_machine.Pin = MockPin