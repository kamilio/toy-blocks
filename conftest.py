import sys
from unittest.mock import MagicMock
import pytest
import asyncio
import os

# Add lib directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

# Mock system time
_current_time = 0

def mock_current_time():
    global _current_time
    return _current_time

def advance_time(seconds):
    global _current_time
    _current_time += seconds

# Mock micropython.const
def mock_const(value):
    return value

mock_micropython = MagicMock()
mock_micropython.const = mock_const
sys.modules['micropython'] = mock_micropython

# Mock machine module's Pin
class MockPin:
    IN = "in"
    OUT = "out"
    PULL_UP = "pull_up"
    PULL_DOWN = "pull_down"
    
    _instances = {}

    def __new__(cls, id, mode=OUT, pull=None):
        existing_instance = cls._instances.get(id)
        if existing_instance is not None:
            return existing_instance
        return super().__new__(cls)
    
    def __init__(self, id, mode=OUT, pull=None):
        if id not in self._instances:
            self.id = id
            self.mode = mode
            self._value = 0
            self.led = self  # Make pin act as its own LED for test compatibility
            self.history = []
            print(f"Created MockPin {id} with mode {mode}")
            self._instances[id] = self

    def value(self, val=None):
        if val is not None:
            val = int(bool(val))  # Convert to 0 or 1
            prev_value = self._value
            self._value = val
            if val != prev_value:  # Only add to history if value actually changed
                print(f"Pin {self.id} value changed from {prev_value} to {val}")
                self.history.append(val)
                print(f"History updated: {self.history}")
            else:
                print(f"Pin {self.id} value unchanged at {val}")
        return self._value
    
    def on(self):
        self.value(1)
        
    def off(self):
        self.value(0)
        
    def toggle(self):
        self.value(not self.value())
    
    @classmethod
    def clear_instances(cls):
        print("Clearing all pin instances")
        cls._instances.clear()

@pytest.fixture(scope='function', autouse=True)
def mock_pin():
    MockPin.clear_instances()
    return MockPin

# Mock machine module's RTC
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

    def ifconfig(self):
        return ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')

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

# Mock uasyncio module with better coroutine handling
async def mock_sleep(delay):
    advance_time(delay)

async def mock_create_task(coro):
    return await coro

mock_uasyncio = MagicMock()
mock_uasyncio.sleep = mock_sleep
mock_uasyncio.create_task = mock_create_task
sys.modules['uasyncio'] = mock_uasyncio

# Mock time module
mock_time = MagicMock()
mock_time.time = mock_current_time
sys.modules['time'] = mock_time

# Reset time before each test
@pytest.fixture(autouse=True)
def reset_time():
    global _current_time
    _current_time = 0

# Mock shift register implementation
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
            raise ValueError("Position must be between 0 and 7")
        if value:
            self.state[0] |= (1 << position)
        else:
            self.state[0] &= ~(1 << position)
        self.pins[position] = value

class ShiftRegisterLed:
    def __init__(self, shift_register, position, active_low=True):  # Default to active_low=True like real implementation
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
