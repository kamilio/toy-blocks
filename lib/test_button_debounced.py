import pytest
import uasyncio
from button import DebouncedButton


@pytest.mark.asyncio
async def test_button_debounce():
    press_count = 0

    async def callback():
        nonlocal press_count
        press_count += 1

    button = DebouncedButton(pin=0, debounce_ms=20, debug=False)
    button.on_button_down(callback)

    # Start released
    button.pin.value(1)
    await button._check_once()

    # First press
    button.pin.value(0)
    await button._check_once()
    assert press_count == 1

    # Second press immediately after (should be ignored due to debounce)
    button.pin.value(1)
    await button._check_once()
    button.pin.value(0)
    await button._check_once()
    assert press_count == 1  # Count should not change due to debounce

    # Wait for debounce period
    await uasyncio.sleep(0.021)  # Just over debounce time

    # Third press after debounce (should be registered)
    button.pin.value(1)
    await button._check_once()
    button.pin.value(0)
    await button._check_once()
    assert press_count == 2  # Should register as a new press


@pytest.mark.asyncio
async def test_debounce_up_event():
    up_count = 0

    async def callback():
        nonlocal up_count
        up_count += 1

    button = DebouncedButton(pin=0, debounce_ms=20, debug=False)
    button.on_button_up(callback)

    # Start pressed
    button.pin.value(0)
    await button._check_once()

    # First release
    button.pin.value(1)
    await button._check_once()
    assert up_count == 1

    # Quick press and release (should be ignored)
    button.pin.value(0)
    await button._check_once()
    button.pin.value(1)
    await button._check_once()
    assert up_count == 1  # Count should not change due to debounce

    # Wait for debounce period
    await uasyncio.sleep(0.021)

    # Another release after debounce
    button.pin.value(0)
    await button._check_once()
    button.pin.value(1)
    await button._check_once()
    assert up_count == 2  # Should register as a new release
