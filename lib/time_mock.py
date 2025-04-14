from unittest.mock import MagicMock

import pytest

# Mock system time
_current_time = 0


def mock_current_time():
    global _current_time
    return _current_time


def advance_time(seconds):
    global _current_time
    _current_time += seconds


# Mock micropython.const
def mock_const(value):
    return value


# Mock time module
mock_time = MagicMock()
mock_time.time = mock_current_time


# Reset time before each test
@pytest.fixture(autouse=True)
def reset_time():
    global _current_time
    _current_time = 0
