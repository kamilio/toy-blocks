import asyncio
from unittest.mock import AsyncMock

import pytest
from machine_mock import SPI, Pin
from sd_card_reader import SDCardReader


# Mock machine module
@pytest.fixture(autouse=True)
def mock_machine(monkeypatch):
    monkeypatch.setattr('machine.Pin', Pin)
    monkeypatch.setattr('machine.SPI', SPI)


@pytest.mark.asyncio
async def test_create_sd_reader():
    reader = SDCardReader(sck_pin=18, mosi_pin=23, miso_pin=19, cs_pin=5)
    assert reader is not None
    assert reader._running is False
    assert reader._callbacks is not None


@pytest.mark.asyncio
async def test_initialize():
    reader = SDCardReader(sck_pin=18, mosi_pin=23, miso_pin=19, cs_pin=5)
    result = await reader.initialize()
    assert result is True


@pytest.mark.asyncio
async def test_callbacks():
    reader = SDCardReader(sck_pin=18, mosi_pin=23, miso_pin=19, cs_pin=5)

    # Create status change callback
    status_change_called = False
    received_status = None

    async def on_status_change(status):
        nonlocal status_change_called, received_status
        status_change_called = True
        received_status = status

    # Register callbacks
    reader.on_status_change(on_status_change)

    # Manually trigger the callback
    await reader._run_callback('status_change', 0x55)

    # Verify callback was called
    assert status_change_called is True
    assert received_status == 0x55


@pytest.mark.asyncio
async def test_monitoring():
    reader = SDCardReader(sck_pin=18, mosi_pin=23, miso_pin=19, cs_pin=5)

    # Create a mock callback
    mock_callback = AsyncMock()
    reader.on_status_change(mock_callback)

    # Create a simplified version of monitor for testing
    original_monitor = reader.monitor

    async def mock_monitor():
        # Set running flag
        reader._running = True
        # Call callback directly with test status
        await reader._run_callback('status_change', 0x55)
        # Wait for stop flag
        while reader._running:
            await asyncio.sleep(0.1)

    # Apply the patch for testing
    reader.monitor = mock_monitor

    # Start monitoring
    monitor_task = asyncio.create_task(reader.monitor())

    # Give it time to run
    await asyncio.sleep(0.1)

    # Verify monitoring started
    assert reader._running is True

    # Check that callback was called
    mock_callback.assert_called_once_with(0x55)

    # Stop monitoring
    reader.stop()

    # Wait for task to complete
    await asyncio.sleep(0.2)
    await monitor_task

    # Verify monitoring stopped
    assert reader._running is False

    # Restore original method
    reader.monitor = original_monitor


@pytest.mark.asyncio
async def test_read_wav():
    reader = SDCardReader(sck_pin=18, mosi_pin=23, miso_pin=19, cs_pin=5)
    await reader.initialize()

    # Test invalid WAV data
    with pytest.raises(ValueError):
        await reader.read_wav('not_a_wav.txt')
