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
    assert debug.led.value() == 1

@pytest.mark.asyncio
async def test_debug_off():
    debug = DebugLed()
    debug.off()
    assert debug.led.value() == 0

@pytest.mark.asyncio
async def test_debug_blink():
    debug = DebugLed()
    await debug.blink(count=2, interval=0.1)
    assert debug.led.value() == 0

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
    assert debug.led.value() == 0