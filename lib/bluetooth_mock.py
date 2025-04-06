from unittest.mock import MagicMock

class MockBLE:
    def __init__(self):
        self._active = False
        self._irq_handler = None
        
    def active(self, state=None):
        if state is not None:
            self._active = state
        return self._active

    def irq(self, handler=None):
        self._irq_handler = handler
        return self._irq_handler

    def gap_advertise(self, interval_us, data=None):
        pass
        
    def gap_scan(self, duration_ms, interval_us, window_us):
        pass

mock_bluetooth = MagicMock()
mock_bluetooth.BLE = MockBLE