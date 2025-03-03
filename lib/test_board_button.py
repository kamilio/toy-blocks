import pytest
import uasyncio
import time
from board_button import BoardButton
from machine import Pin
from unittest.mock import AsyncMock, patch

@pytest.fixture
def board_button():
    button = BoardButton()
    button.boot_button.value(1)  # Initialize to not pressed
    button._last_press_time = 0  # Reset debounce timer
    return button

def test_board_button_initialization(board_button):
    assert isinstance(board_button.boot_button, Pin)
    assert board_button._running == False

def test_is_boot_pressed(board_button):
    board_button.boot_button.value(0)  # Pressed (pulled low)
    assert board_button.is_boot_pressed() == True
    
    board_button.boot_button.value(1)  # Not pressed (pulled high)
    assert board_button.is_boot_pressed() == False

@pytest.mark.asyncio
async def test_monitor_with_async_callback(board_button):
    call_count = 0
    
    async def async_callback():
        nonlocal call_count
        call_count += 1
        yield None
        
    with patch('uasyncio.create_task', new_callable=AsyncMock) as mock_create_task:
        task = AsyncMock()
        task.__iter__ = lambda: (yield None)
        mock_create_task.return_value = task
        board_button.on_press(async_callback)
        
        # Initial state - not pressed
        assert board_button._was_pressed == False
        
        # First press
        board_button.boot_button.value(0)  # Press
        await board_button._check_once()
        assert mock_create_task.called
        mock_create_task.reset_mock()
        
        # Release
        board_button.boot_button.value(1)  # Release
        await board_button._check_once()
        assert not mock_create_task.called
        
        # Second press (after debounce)
        board_button._last_press_time = 0  # Clear debounce
        board_button.boot_button.value(0)  # Press again
        await board_button._check_once()
        assert mock_create_task.called

@pytest.mark.asyncio
async def test_debounce(board_button):
    calls = 0
    task = AsyncMock()
    task.__iter__ = lambda: (yield None)
    
    async def async_callback():
        nonlocal calls
        calls += 1
        yield None
    
    board_button.on_press(async_callback)
    
    # Test debounce and reset
    with patch('uasyncio.create_task', new_callable=AsyncMock) as mock_create_task:
        # First press
        board_button.boot_button.value(0)
        await board_button._check_once()
        assert mock_create_task.call_count == 1
        
        # Press again immediately (should be ignored due to debounce)
        await board_button._check_once()
        assert mock_create_task.call_count == 1
        
        # Release button
        board_button.boot_button.value(1)
        await board_button._check_once()

        # Press again after debounce reset
        board_button.boot_button.value(0)  # Press again
        board_button._last_press_time = 0
        await board_button._check_once()
        assert mock_create_task.call_count == 2