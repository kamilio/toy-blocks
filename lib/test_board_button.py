import pytest
import uasyncio
from board_button import BoardButton
from board_config import BoardConfig
from machine import Pin

@pytest.mark.asyncio
async def test_board_button_initialization():
    config = BoardConfig()
    button = BoardButton(config)
    assert isinstance(button.pin, Pin)
    assert not button._running
    
@pytest.mark.asyncio
async def test_monitor_buttons_delegates_to_base():
    button = BoardButton(BoardConfig())
    
    uasyncio.create_task(button.monitor())
    async def stop_after_delay():
        await uasyncio.sleep(0.2)
        button.stop()
    
    await stop_after_delay()
    assert not button._running