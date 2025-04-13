from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from auto_shutdown import AutoShutdown
import sys
import uasyncio

@pytest.mark.asyncio
async def test_init():
    """Test initialization sets correct timeout"""
    with patch('auto_shutdown.time', return_value=100):
        # Patch any direct access to the AudioAmplifier if needed
        with patch('lib.audio_amplifier.AudioAmplifier._monitor', new_callable=AsyncMock):
            auto = AutoShutdown(timeout=60)
            assert auto.timeout == 60
            assert auto.start_time == 100
    assert auto.start_time > 0

@pytest.mark.asyncio
async def test_no_deepsleep_before_timeout():
    """Test deepsleep not called before timeout"""
    with patch('auto_shutdown.time', side_effect=[100, 150]) as mock_time, \
         patch('lib.audio_amplifier.AudioAmplifier._monitor', new_callable=AsyncMock):
        mock_machine = sys.modules['machine']
        
        auto = AutoShutdown(timeout=60)
        await auto.maybe_deepsleep()
        
        assert not mock_machine.deepsleep.called

@pytest.mark.asyncio
async def test_deepsleep_after_timeout():
    """Test deepsleep called after timeout"""
    with patch('auto_shutdown.time', side_effect=[100, 180]) as mock_time:
        mock_machine = sys.modules['machine']
        
        auto = AutoShutdown(timeout=60)
        assert auto.start_time == 100
        await auto.maybe_deepsleep()
        
        assert mock_machine.deepsleep.call_count == 1

@pytest.mark.asyncio
async def test_monitor_stops():
    """Test monitor can be stopped"""
    with patch('auto_shutdown.time', return_value=100), \
         patch('uasyncio.sleep', new_callable=AsyncMock) as mock_sleep:

        auto = AutoShutdown(timeout=60)
        
        # Start monitoring and immediately stop
        auto._running = True
        await auto.maybe_deepsleep()
        auto.stop()
        assert not auto._running
        assert mock_sleep.called is False

@pytest.mark.asyncio
async def test_reset_timer():
    """Test timer can be reset"""
    mock_machine = sys.modules['machine']
    mock_machine.deepsleep.reset_mock()
    with patch('auto_shutdown.time', side_effect=[100, 150, 200]) as mock_time:
        auto = AutoShutdown(timeout=60)
        assert auto.start_time == 100
        auto.reset_timer()
        assert auto.start_time == 150
        await auto.maybe_deepsleep()
