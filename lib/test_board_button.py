import pytest
import uasyncio
from board_button import BoardButton
from machine import Pin

@pytest.mark.asyncio
async def test_board_button_initialization():
    button = BoardButton()
    assert isinstance(button.pin, Pin)
    assert not button._running
    
@pytest.mark.asyncio
async def test_monitor_buttons_delegates_to_base():
    button = BoardButton()
    
    uasyncio.create_task(button.monitor())
    async def stop_after_delay():
        await uasyncio.sleep(0.2)
        button.stop()
    
    await stop_after_delay()
    assert not button._running