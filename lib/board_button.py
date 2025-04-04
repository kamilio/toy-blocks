from machine import Pin
import uasyncio
import time
from button import DebouncedButton

class BoardButton(DebouncedButton):
    def __init__(self, board_config, **kwargs):
        super().__init__(pin=board_config.board_button_pin, **kwargs)
