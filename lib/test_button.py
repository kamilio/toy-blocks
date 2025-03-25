import pytest
from button import Button
from machine import Pin
import uasyncio
import time
from unittest.mock import patch

@pytest.mark.asyncio
async def test_button_init():
    # Pass debug=False to avoid logging during tests
    button = Button(pin=0, debug=False)
    assert not button._running
    assert button._callbacks['single'] is None
    assert button._callbacks['down'] is None
    assert button._callbacks['up'] is None

@pytest.mark.asyncio
async def test_button_press_callback():
    called = False
    async def callback():
        nonlocal called
        called = True
        
    button = Button(pin=0, debug=False)
    button.on_press(callback)
    # Start with button released
    button.pin.value(1)
    await button._check_once()
    # Press the button
    button.pin.value(0)
    await button._check_once()
    assert called

@pytest.mark.asyncio
async def test_button_debounce():
    press_count = 0
    async def callback():
        nonlocal press_count
        press_count += 1
        
    button = Button(pin=0, debug=False)
    button.on_press(callback)
    # Start released
    button.pin.value(1)
    await button._check_once()
    # First press
    button.pin.value(0)
    await button._check_once()
    # Second press without enough time passing
    await button._check_once()
    assert press_count == 1

@pytest.mark.asyncio
async def test_double_click():
    single_called = False
    double_called = False
    
    async def on_single():
        nonlocal single_called
        single_called = True
        
    async def on_double():
        nonlocal double_called
        double_called = True
    
    button = Button(pin=0, debug=False)
    button.on_press(on_single)
    button.on_double_press(on_double)
    
    # Start released
    button.pin.value(1)
    await button._check_once()
    
    # First click
    button.pin.value(0)  # Press
    await button._check_once()
    button.pin.value(1)  # Release
    await button._check_once()
    
    # Second click within double click delay
    button.pin.value(0)  # Press
    await button._check_once()
    button.pin.value(1)  # Release
    await button._check_once()
    
    # Wait for double click timeout
    await uasyncio.sleep(button._double_click_delay + 0.1)
    await button._check_once()
    
    assert not single_called
    assert double_called

@pytest.mark.asyncio
async def test_triple_click():
    triple_called = False
    
    async def on_triple():
        nonlocal triple_called
        triple_called = True
    
    button = Button(pin=0, debug=False)
    button.on_triple_press(on_triple)
    
    # Start released
    button.pin.value(1)
    await button._check_once()
    
    for _ in range(3):
        button.pin.value(0)  # Press
        await button._check_once()
        button.pin.value(1)  # Release
        await button._check_once()
    
    await uasyncio.sleep(button._double_click_delay + 0.1)
    await button._check_once()
    
    assert triple_called

@pytest.mark.asyncio
async def test_long_press():
    long_called = False
    
    async def on_long():
        nonlocal long_called
        long_called = True
    
    button = Button(pin=0, debug=False)
    button.on_long_press(on_long)
    
    # Start released
    button.pin.value(1)
    await button._check_once()
    
    # Press and hold
    button.pin.value(0)
    await button._check_once()
    await uasyncio.sleep(button._long_press_time + 0.1)
    await button._check_once()  # Should detect long press
    button.pin.value(1)  # Release
    await button._check_once()
    
    assert long_called

@pytest.mark.asyncio
async def test_button_down_event():
    down_called = False
    
    async def on_down():
        nonlocal down_called
        down_called = True
    
    button = Button(pin=0, debug=False)
    button.on_button_down(on_down)
    
    # Start released
    button.pin.value(1)
    await button._check_once()
    
    # Press the button
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
    
    # Start released
    button.pin.value(1)
    await button._check_once()
    
    # Press the button
    button.pin.value(0)
    await button._check_once()
    
    # Release the button
    button.pin.value(1)
    await button._check_once()
    
    assert up_called

@pytest.mark.asyncio
async def test_button_monitor_stops():
    button = Button(pin=0, debug=False)
    
    async def stop_after_delay():
        await uasyncio.sleep(0.2)
        button.stop()
    
    monitor_task = uasyncio.create_task(button.monitor())
    stop_task = uasyncio.create_task(stop_after_delay())
    await stop_task
    assert not button._running
