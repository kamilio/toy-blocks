from unittest.mock import MagicMock
from time_mock import advance_time

async def mock_sleep(delay):
    advance_time(delay)

async def mock_create_task(coro):
    return await coro

mock_uasyncio = MagicMock()
mock_uasyncio.sleep = mock_sleep
mock_uasyncio.create_task = mock_create_task