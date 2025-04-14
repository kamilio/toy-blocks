import inspect
from unittest.mock import AsyncMock, MagicMock

from time_mock import advance_time


# Create a callable mock that tracks calls
async def _mock_sleep_impl(seconds):
    advance_time(seconds)


mock_sleep = AsyncMock(side_effect=_mock_sleep_impl)


def reset_mock_sleep():
    """Reset the mock sleep call count before each test"""
    mock_sleep.reset_mock()


# Improved version that properly handles coroutines
async def mock_create_task(coro):
    if inspect.iscoroutine(coro):
        return await coro
    # For cases where it's not a coroutine but a regular function
    return coro


# Global registry to track tasks that might not be awaited
pending_tasks = []


# Create task function that handles proper cleanup
def create_task_with_cleanup(coro):
    """Create task with proper cleanup to avoid coroutine warnings."""
    if inspect.iscoroutine(coro):
        # For real coroutines, we need to ensure they're awaited
        global pending_tasks
        result = mock_create_task(coro)
        pending_tasks.append(result)
        return result
    return coro


mock_uasyncio = MagicMock()
mock_uasyncio.sleep = mock_sleep
mock_uasyncio.create_task = create_task_with_cleanup
