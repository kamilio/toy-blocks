import pytest
import uasyncio
from button import Button


@pytest.mark.asyncio
async def test_button_init():
    button = Button(pin=0, debug=False)
    assert not button._running
    assert button._callbacks['down'] is None
    assert button._callbacks['up'] is None


@pytest.mark.asyncio
async def test_button_down_event():
    down_called = False

    async def on_down():
        nonlocal down_called
        down_called = True

    button = Button(pin=0, debug=False)
    button.on_button_down(on_down)

    button.pin.value(1)
    await button._check_once()

    button.pin.value(0)
    await button._check_once()

    assert down_called


@pytest.mark.asyncio
async def test_button_up_event():
    up_called = False

    async def on_up():
        nonlocal up_called
        up_called = True

    button = Button(pin=0, debug=False)
    button.on_button_up(on_up)

    button.pin.value(1)
    await button._check_once()

    button.pin.value(0)
    await button._check_once()

    button.pin.value(1)
    await button._check_once()

    assert up_called


@pytest.mark.asyncio
async def test_button_monitor_stops():
    button = Button(pin=0, debug=False)

    # Create a real awaitable callback
    down_callback_called = False

    async def down_callback():
        nonlocal down_callback_called
        down_callback_called = True

    # Register the callback
    button.on_button_down(down_callback)

    # Set up a function to stop the monitor after a delay
    async def stop_after_delay():
        await uasyncio.sleep(0.2)
        button.stop()

    # Create a task for the monitor
    # Since we want to manually create a monitor task, let's do it without mocking

    async def start_and_stop_monitor():
        # Start monitoring in a way we can control
        button._running = True
        # First simulate a button press to trigger callback
        button.pin.value(0)  # simulate press (active low)
        await button._check_once()
        # Then stop after delay
        await stop_after_delay()

    # Run our controlled test scenario
    await start_and_stop_monitor()

    # Button should be stopped
    assert not button._running


@pytest.mark.asyncio
async def test_button_press_tracking():
    button = Button(pin=0, debug=False)

    # Initially not pressed
    assert not button.was_pressed
    assert not button.consume_was_pressed()

    # Press button
    button.pin.value(0)
    await button._check_once()
    assert not button.was_pressed  # Still not marked as pressed until released

    # Release button
    button.pin.value(1)
    await button._check_once()
    assert button.was_pressed  # Now marked as was pressed

    # Check and reset state
    assert button.consume_was_pressed()
    assert not button.was_pressed  # State was reset
    assert not button.consume_was_pressed()  # Second check should return False
