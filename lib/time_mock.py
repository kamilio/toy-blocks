from unittest.mock import MagicMock
import pytest

_current_time_us = 0

def ticks_ms():
    return _current_time_us // 1000

def ticks_us():
    return _current_time_us

def ticks_cpu():
    return _current_time_us

def ticks_add(ticks, delta):
    return ticks + delta

def ticks_diff(ticks1, ticks2):
    return ticks1 - ticks2

def sleep(seconds):
    global _current_time_us
    _current_time_us += int(seconds * 1_000_000)

def sleep_ms(ms):
    global _current_time_us
    _current_time_us += ms * 1000

def sleep_us(us):
    global _current_time_us
    _current_time_us += us

def time():
    return _current_time_us / 1_000_000  # Return float seconds

def localtime(secs=None):
    if secs is None:
        secs = int(time())
    return (2000, 1, 1, 0, 0, secs, 0, 0)

def mktime(tuple):
    return tuple[5]

def gmtime(secs=None):
    return localtime(secs)

def set_time(us):
    global _current_time_us
    _current_time_us = us

def advance_time(seconds):
    global _current_time_us
    _current_time_us += int(float(seconds) * 1_000_000)

def mock_const(value):
    return value

mock_time = MagicMock()
mock_time.time = time
mock_time.sleep = sleep
mock_time.sleep_ms = sleep_ms
mock_time.sleep_us = sleep_us
mock_time.ticks_ms = ticks_ms 
mock_time.ticks_us = ticks_us
mock_time.ticks_cpu = ticks_cpu
mock_time.ticks_add = ticks_add
mock_time.ticks_diff = ticks_diff
mock_time.localtime = localtime
mock_time.mktime = mktime
mock_time.gmtime = gmtime

@pytest.fixture(autouse=True)
def reset_time():
    global _current_time_us
    _current_time_us = 0
