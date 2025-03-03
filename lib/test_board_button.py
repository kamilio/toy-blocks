import pytest
import uasyncio
import time
from board_button import BoardButton
from machine import Pin
from unittest.mock import AsyncMock, MagicMock

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
async def test_monitor_with_sync_callback(board_button):
    callback_called = 0
    
    def on_press():
        nonlocal callback_called
        callback_called += 1
        print(f"Callback called: {callback_called}")
    
    board_button.on_press(on_press)
    
    print("\nStarting sync callback test")
    
    # First press
    board_button.boot_button.value(0)
    await board_button._check_once()
    assert callback_called == 1
    
    # Release
    board_button.boot_button.value(1)
    await board_button._check_once()
    
    # Wait to avoid debounce
    board_button._last_press_time = 0
    
    # Second press
    board_button.boot_button.value(0)
    await board_button._check_once()
    assert callback_called == 2

@pytest.mark.asyncio
async def test_monitor_with_async_callback(board_button):
    callback = AsyncMock()
    board_button.on_press(callback)
    
    print("\nStarting async callback test")
    
    # First press
    board_button.boot_button.value(0)
    await board_button._check_once()
    assert callback.await_count == 1
    
    # Release
    board_button.boot_button.value(1)
    await board_button._check_once()
    
    # Wait to avoid debounce
    board_button._last_press_time = 0
    
    # Second press
    board_button.boot_button.value(0)
    await board_button._check_once()
    assert callback.await_count == 2

@pytest.mark.asyncio
async def test_debounce(board_button):
    callback_called = 0
    
    def on_press():
        nonlocal callback_called
        callback_called += 1
    
    board_button.on_press(on_press)
    
    # First press
    board_button.boot_button.value(0)
    await board_button._check_once()
    assert callback_called == 1
    
    # Immediate second press should be ignored due to debounce
    board_button.boot_button.value(1)  # Release
    await board_button._check_once()
    board_button.boot_button.value(0)  # Press again
    await board_button._check_once()
    assert callback_called == 1  # Should not increment