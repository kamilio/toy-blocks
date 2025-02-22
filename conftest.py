import sys
from unittest.mock import MagicMock

# Mock micropython.const
def mock_const(value):
    return value

mock_micropython = MagicMock()
mock_micropython.const = mock_const
sys.modules['micropython'] = mock_micropython

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

# Mock machine module
mock_machine = MagicMock()
mock_machine.Pin = MockPin
sys.modules['machine'] = mock_machine

# Mock bluetooth module for BLE tests
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
sys.modules['bluetooth'] = mock_bluetooth

# Mock network module
class MockWLAN:
    STA_IF = 1
    
    def __init__(self, interface):
        self._active = False
        self._connected = False
        
    def active(self, state=None):
        if state is not None:
            self._active = state
        return self._active
        
    def isconnected(self):
        return self._connected
        
    def connect(self, ssid, password):
        self._connected = True
        
    def disconnect(self):
        self._connected = False

mock_network = MagicMock()
mock_network.WLAN = MockWLAN
sys.modules['network'] = mock_network

# Mock urequests module
class MockResponse:
    def __init__(self, json_data):
        self._json_data = json_data
        
    def json(self):
        return self._json_data
        
    def close(self):
        pass

def mock_get(url):
    return MockResponse({"test": "config"})

mock_urequests = MagicMock()
mock_urequests.get = mock_get
sys.modules['urequests'] = mock_urequests