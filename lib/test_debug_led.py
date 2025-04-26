from unittest.mock import MagicMock, patch

import pytest
from debug_led import DebugLed


@pytest.mark.asyncio
async def test_debug_init():
    debug = DebugLed(pin_config=None, pin=2, active_low=False)
    assert debug.led.mode == debug.led.OUT


@pytest.mark.asyncio
async def test_debug_on():
    debug = DebugLed(pin_config=None, pin=2, active_low=False)
    debug.on()
    assert debug._get_value() == 1


@pytest.mark.asyncio
async def test_debug_off():
    debug = DebugLed(pin_config=None, pin=2, active_low=False)
    debug.off()
    assert debug._get_value() == 0


@pytest.mark.asyncio
async def test_debug_on_active_low():
    debug = DebugLed(pin_config=None, pin=2, active_low=True)
    debug.on()
    assert debug._get_value() == 1


@pytest.mark.asyncio
async def test_debug_off_active_low():
    debug = DebugLed(pin_config=None, pin=2, active_low=True)
    debug.off()
    assert debug._get_value() == 0


@pytest.mark.asyncio
async def test_debug_blink_active_low():
    debug = DebugLed(pin_config=None, pin=2, active_low=True)
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == debug._prev_state


@pytest.mark.asyncio
async def test_debug_blink_preserves_state():
    debug = DebugLed(pin_config=None, pin=2, active_low=False)
    debug.on()
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == 1

    debug.off()
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == 0


@pytest.mark.asyncio
async def test_debug_blink():
    debug = DebugLed(pin_config=None, pin=2, active_low=False)
    initial_state = debug._get_value()
    await debug.blink(count=2, interval=0.1)
    assert debug._get_value() == initial_state


async def mock_sleep_with_interrupt(*args):
    raise KeyboardInterrupt


@pytest.mark.asyncio
async def test_blink_forever_start():
    debug = DebugLed(pin_config=None, pin=2, active_low=False)
    try:
        with patch('uasyncio.sleep', mock_sleep_with_interrupt):
            await debug.blink_forever(interval=0.1)
    except KeyboardInterrupt:
        pass
    assert debug._blink_forever


@pytest.mark.asyncio
async def test_stop_blinking():
    debug = DebugLed(pin_config=None, pin=2, active_low=False)
    debug._blink_forever = True
    debug.stop_blinking()
    assert not debug._blink_forever


@pytest.mark.asyncio
async def test_debug_blink_three_times_active_low(mock_pin):
    print('\nStarting blink test...')
    pin = 2
    mock_pin = mock_pin(pin)  # Get pin instance before creating DebugLed
    print(f'Initial pin state - value: {mock_pin.value()}, history: {mock_pin.history}')

    led = DebugLed(pin_config=None, pin=pin, active_low=True)
    print(f'Created DebugLed with pin={pin}, active_low=True')

    # Mock sleep to be synchronous
    async def mock_sleep(t):
        print(f'Sleep called, current pin value: {mock_pin.value()}, history: {mock_pin.history}')
        return

    with patch('uasyncio.sleep', mock_sleep):
        await led.blink(count=3, interval=0.1)

    print(f'Final pin value: {mock_pin.value()}')
    print(f'Final pin history: {mock_pin.history}')
    # Look for 3 on-off cycles plus final state restore:
    # 1. Initial on, off
    # 2. Second on, off
    # 3. Third on, off
    # 4. Final state restore
    assert len(mock_pin.history) == 7
