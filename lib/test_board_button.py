import pytest
from board_button import BoardButton
from board_config import BoardConfig

class MockBoardConfig:
    def __init__(self):
        self.board_button_pin = 5

@pytest.mark.asyncio
async def test_board_button_initialization():
    button = BoardButton(MockBoardConfig())
    button.pin.value(1)  # Set initial state to released
    assert not button.is_pressed()

@pytest.mark.asyncio
async def test_button_press_callback():
    press_count = 0
    async def on_press():
        nonlocal press_count
        press_count += 1

    button = BoardButton(MockBoardConfig())
    button.pin.value(1)  # Start released
    await button._check_once()
    button.on_press(on_press)
    
    button.pin.value(0)  # Press button
    await button._check_once()
    button.pin.value(1)  # Release button
    await button._check_once()

    assert press_count == 1