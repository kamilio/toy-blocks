from debug import Debug
from pins import BUILTIN_LED
from unittest.mock import patch, MagicMock
import time

def test_debug_init():
    debug = Debug()
    assert debug.led.mode == debug.led.OUT
    assert not debug._blink_forever

def test_debug_on():
    debug = Debug()
    debug.on()
    assert debug.led.value() == 1

def test_debug_off():
    debug = Debug()
    debug.off()
    assert debug.led.value() == 0

def test_debug_blink():
    debug = Debug()
    debug.blink(count=2, interval=0.1)
    assert debug.led.value() == 0  # Should end in off state

def mock_sleep_with_interrupt(*args):
    raise InterruptedError("Test complete")

def test_blink_forever_start():
    debug = Debug()
    with patch('time.sleep', mock_sleep_with_interrupt):
        try:
            debug.blink_forever(interval=0.1)
        except InterruptedError:
            pass
    assert debug._blink_forever == True
    assert debug.led.value() == 1  # LED should be on when interrupted

def test_stop_blinking():
    debug = Debug()
    debug._blink_forever = True
    debug.stop_blinking()
    assert debug._blink_forever == False
    assert debug.led.value() == 0