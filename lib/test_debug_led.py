from debug_led import DebugLed
from pins import BUILTIN_LED
from unittest.mock import patch
import pytest
import uasyncio

@pytest.mark.asyncio
async def test_debug_init():
    debug = DebugLed()
    assert debug.led.mode == debug.led.OUT

@pytest.mark.asyncio
async def test_debug_on():
    debug = DebugLed()
    debug.on()
    assert debug._get_value() == 1

@pytest.mark.asyncio
async def test_debug_off():
    debug = DebugLed()
    debug.off()
    assert debug._get_value() == 0

@pytest.mark.asyncio
async def test_debug_on_active_low():
    debug = DebugLed(active_low=True)
    debug.on()
    assert debug._get_value() == 1

@pytest.mark.asyncio
async def test_debug_off_active_low():
    debug = DebugLed(active_low=True)
    debug.off()
    assert debug._get_value() == 0

@pytest.mark.asyncio
async def test_debug_blink_active_low():
    debug = DebugLed(active_low=True)
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == debug._prev_state

@pytest.mark.asyncio
async def test_debug_blink_preserves_state():
    debug = DebugLed()
    debug.on()
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == 1

    debug.off()
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == 0

@pytest.mark.asyncio
async def test_debug_blink():
    debug = DebugLed()
    initial_state = debug._get_value()
    await debug.blink(count=2, interval=0.1)
    assert debug._get_value() == initial_state

async def mock_sleep_with_interrupt(*args):
    raise KeyboardInterrupt

@pytest.mark.asyncio
async def test_blink_forever_start():
    debug = DebugLed()
    with patch('uasyncio.sleep', mock_sleep_with_interrupt):
        try:
            await debug.blink_forever(interval=0.1)
        except KeyboardInterrupt:
            pass
    assert debug._blink_forever == True

@pytest.mark.asyncio
async def test_stop_blinking():
    debug = DebugLed()
    debug._blink_forever = True
    debug.stop_blinking()
    assert debug._blink_forever == False

class MockPinWithHistory:
    OUT = "out"
    def __init__(self, id, mode):
        self.id = id
        self.mode = mode
        self._value = 0
        self.history = []

    def value(self, val=None):
        if val is not None:
            self._value = val
            self.history.append(val)
        return self._value

@pytest.fixture
def mock_pin_with_history(monkeypatch):
    pins = {}
    def mock_Pin(pin, mode):
        pins[pin] = MockPinWithHistory(pin, mode)
        return pins[pin]
    monkeypatch.setattr('machine.Pin', mock_Pin)
    return lambda pin: pins[pin]

@pytest.mark.asyncio
async def test_debug_blink_three_times_active_low(mock_pin_with_history):
    pin = 2
    debug = DebugLed(pin=pin, active_low=True)
    await debug.blink(count=3, interval=0.1)
    assert len(mock_pin_with_history(pin).history) == 7  # 3 on-off cycles plus final state restore