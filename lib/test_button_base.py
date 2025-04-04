import pytest
from button import Button
from machine import Pin
import uasyncio

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
    
    async def stop_after_delay():
        await uasyncio.sleep(0.2)
        button.stop()
    
    monitor_task = uasyncio.create_task(button.monitor())
    stop_task = uasyncio.create_task(stop_after_delay())
    await stop_task
    assert not button._running