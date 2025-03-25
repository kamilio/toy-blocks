from board_config import BoardConfig
from machine import Pin
from button import Button

class BoardButton(Button):
    def __init__(self, config: BoardConfig):
        self.config = config
        super().__init__(
            pin=self.config.BOOT_BUTTON, 
            pin_mode=Pin.IN,
            pull=Pin.PULL_UP
        )
