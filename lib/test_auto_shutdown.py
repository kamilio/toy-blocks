from unittest.mock import patch
import pytest
from auto_shutdown import AutoShutdown
import sys

def test_init():
    """Test initialization sets correct timeout"""
    auto = AutoShutdown(timeout=60)
    assert auto.timeout == 60
    assert auto.start_time > 0

def test_no_deepsleep_before_timeout():
    """Test deepsleep not called before timeout"""
    with patch('auto_shutdown.time', side_effect=[100, 150]) as mock_time:  # Start time, check time (50s elapsed)
        mock_machine = sys.modules['machine']
        
        auto = AutoShutdown(timeout=60)
        auto.maybe_deepsleep()
        
        assert not mock_machine.deepsleep.called

def test_deepsleep_after_timeout():
    """Test deepsleep called after timeout"""
    with patch('auto_shutdown.time', side_effect=[100, 180]) as mock_time:  # First call 100, second call 180 (80s elapsed > 60s timeout)
        mock_machine = sys.modules['machine']
        
        auto = AutoShutdown(timeout=60)
        assert auto.start_time == 100  # Verify start_time is set correctly
        auto.maybe_deepsleep()
        
        assert mock_machine.deepsleep.call_count == 1