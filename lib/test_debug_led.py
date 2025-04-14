import contextlib
from unittest.mock import MagicMock, patch

import pytest
from board_config import BoardConfig
from debug_led import DebugLed


# Create a mock BoardConfig for testing
@pytest.fixture
def mock_board_config():
    mock_config = MagicMock(spec=BoardConfig)
    mock_config.LED_PIN = 2
    mock_config.is_builtin_led_active_low.return_value = False
    return mock_config


@pytest.mark.asyncio
async def test_debug_init(mock_board_config):
    debug = DebugLed(mock_board_config)
    assert debug.led.mode == debug.led.OUT


@pytest.mark.asyncio
async def test_debug_on(mock_board_config):
    debug = DebugLed(mock_board_config)
    debug.on()
    assert debug._get_value() == 1


@pytest.mark.asyncio
async def test_debug_off(mock_board_config):
    debug = DebugLed(mock_board_config)
    debug.off()
    assert debug._get_value() == 0


@pytest.mark.asyncio
async def test_debug_on_active_low(mock_board_config):
    debug = DebugLed(mock_board_config, active_low=True)
    debug.on()
    assert debug._get_value() == 1


@pytest.mark.asyncio
async def test_debug_off_active_low(mock_board_config):
    debug = DebugLed(mock_board_config, active_low=True)
    debug.off()
    assert debug._get_value() == 0


@pytest.mark.asyncio
async def test_debug_blink_active_low(mock_board_config):
    debug = DebugLed(mock_board_config, active_low=True)
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == debug._prev_state


@pytest.mark.asyncio
async def test_debug_blink_preserves_state(mock_board_config):
    debug = DebugLed(mock_board_config)
    debug.on()
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == 1

    debug.off()
    await debug.blink(count=1, interval=0.1)
    assert debug._get_value() == 0


@pytest.mark.asyncio
async def test_debug_blink(mock_board_config):
    debug = DebugLed(mock_board_config)
    initial_state = debug._get_value()
    await debug.blink(count=2, interval=0.1)
    assert debug._get_value() == initial_state


async def mock_sleep_with_interrupt(*args):
    raise KeyboardInterrupt


@pytest.mark.asyncio
async def test_blink_forever_start(mock_board_config):
    debug = DebugLed(mock_board_config)
    with patch('uasyncio.sleep', mock_sleep_with_interrupt), contextlib.suppress(KeyboardInterrupt):
        await debug.blink_forever(interval=0.1)
    assert debug._blink_forever


@pytest.mark.asyncio
async def test_stop_blinking(mock_board_config):
    debug = DebugLed(mock_board_config)
    debug._blink_forever = True
    debug.stop_blinking()
    assert not debug._blink_forever


@pytest.mark.asyncio
async def test_debug_blink_three_times_active_low(mock_pin, mock_board_config):
    print('\nStarting blink test...')
    pin = 2
    mock_pin = mock_pin(pin)  # Get pin instance before creating DebugLed
    print(f'Initial pin state - value: {mock_pin.value()}, history: {mock_pin.history}')

    # Configure mock to return the custom pin
    mock_board_config.LED_PIN = pin

    led = DebugLed(mock_board_config, active_low=True)
    print(f'Created DebugLed with board_config, pin={pin}, active_low=True')

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
