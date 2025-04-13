
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from lib.pin_mock import MockPin
from lib.hardware_mock import MockPWM
from lib.audio_amplifier import AudioAmplifier
from lib.sd_card_reader import SDCardReader

# Mock machine module
@pytest.fixture(autouse=True)
def mock_machine(monkeypatch):
    monkeypatch.setattr('machine.Pin', MockPin)
    monkeypatch.setattr('machine.PWM', MockPWM)


@pytest.mark.asyncio
async def test_audio_amplifier_initialization():
    # Test default initialization with PAM8403
    amp = AudioAmplifier(data_pin=25)
    assert amp.amp_type == AudioAmplifier.PAM8403
    assert amp.sample_rate == 44100
    assert amp.volume == 50
    assert amp._playing == False
    assert amp._running == False
    
    # Test initialization with MAX98357A and shutdown pin
    amp2 = AudioAmplifier(data_pin=25, amp_type=AudioAmplifier.MAX98357A, shutdown_pin=26)
    assert amp2.amp_type == AudioAmplifier.MAX98357A
    assert amp2.shutdown_pin is not None


@pytest.mark.asyncio
async def test_volume_control():
    amp = AudioAmplifier(data_pin=25)
    
    # Test valid volume range
    amp.volume = 75
    assert amp.volume == 75
    
    # Test invalid volume (should not change)
    amp.volume = 150
    assert amp.volume == 75
    
    amp.volume = -10
    assert amp.volume == 75


@pytest.mark.asyncio
async def test_enable_disable():
    # Test with shutdown pin (PAM8403)
    amp = AudioAmplifier(data_pin=25, shutdown_pin=26)
    
    # Verify shutdown_pin is not None
    assert amp.shutdown_pin is not None
    
    # Initially disabled
    assert amp.shutdown_pin.value() == 0
    
    # Enable
    amp.enable()
    assert amp.shutdown_pin.value() == 1
    
    # Disable
    amp.disable()
    assert amp.shutdown_pin.value() == 0
    
    # Test with MAX98357A
    amp2 = AudioAmplifier(data_pin=25, amp_type=AudioAmplifier.MAX98357A, shutdown_pin=26)
    
    # Verify shutdown_pin is not None
    assert amp2.shutdown_pin is not None
    
    # Initially enabled for MAX98357A
    assert amp2.shutdown_pin.value() == 1
    
    # Disable
    amp2.disable()
    assert amp2.shutdown_pin.value() == 0
    
    # Enable again
    amp2.enable()
    assert amp2.shutdown_pin.value() == 1


@pytest.mark.asyncio
async def test_play_wav_with_mock_sd_reader():
    amp = AudioAmplifier(data_pin=25)
    
    # Create mock SD reader with read_wav method
    mock_sd_reader = MagicMock(spec=SDCardReader)
    mock_read_wav = AsyncMock()
    
    # Mock audio data (simple 8-bit samples)
    sample_rate = 8000
    audio_data = bytes([128, 200, 150, 100, 50, 75, 100, 150])
    mock_read_wav.return_value = (sample_rate, audio_data)
    
    # Attach mock read_wav method to SD reader
    mock_sd_reader.read_wav = mock_read_wav
    
    # Test playing WAV file
    result = await amp.play_wav(mock_sd_reader, "test.wav")
    assert result == True
    mock_read_wav.assert_called_once_with("test.wav")
    
    # Check that playback started
    assert amp._playing == True
    assert amp._current_audio_data == audio_data
    assert amp.sample_rate == sample_rate
    
    # Clean up
    await amp.stop_playback()
    assert amp._playing == False


@pytest.mark.asyncio
async def test_play_nonexistent_wav():
    amp = AudioAmplifier(data_pin=25)
    
    # Create mock SD reader that returns None for non-existent file
    mock_sd_reader = MagicMock(spec=SDCardReader)
    mock_read_wav = AsyncMock(return_value=None)
    mock_sd_reader.read_wav = mock_read_wav
    
    # Test playing non-existent WAV file
    result = await amp.play_wav(mock_sd_reader, "nonexistent.wav")
    assert result == False
    mock_read_wav.assert_called_once_with("nonexistent.wav")
    assert amp._playing == False


@pytest.mark.asyncio
async def test_monitoring():
    amp = AudioAmplifier(data_pin=25)
    
    # Create a callback to track status updates
    received_status = None
    
    async def test_callback(status):
        nonlocal received_status
        received_status = status
    
    # Register the callback using on_status_change
    amp.on_status_change(test_callback)
    
    # Manually call the _run_callback with a test status
    status = {
        "playing": False,
        "volume": amp.volume,
        "type": amp.amp_type,
        "sample_rate": amp.sample_rate
    }
    
    # Call the _run_callback method with our test status
    await amp._run_callback('status_change', status)
    
    # Verify callback was called with status
    assert received_status is not None
    assert "playing" in received_status
    assert "volume" in received_status
    assert "type" in received_status


@pytest.mark.asyncio
async def test_event_callbacks():
    amp = AudioAmplifier(data_pin=25)
    
    # Create tracking variables for each event
    status_change_called = False
    playback_started_called = False
    playback_completed_called = False
    error_called = False
    
    # Create callback functions
    async def on_status_change(status):
        nonlocal status_change_called
        status_change_called = True
    
    async def on_playback_started(status):
        nonlocal playback_started_called
        playback_started_called = True
    
    async def on_playback_completed(status):
        nonlocal playback_completed_called
        playback_completed_called = True
    
    # Register callbacks
    amp.on_status_change(on_status_change)
    amp.on_playback_started(on_playback_started)
    amp.on_playback_completed(on_playback_completed)
    
    # Test each callback
    await amp._run_callback('status_change', {"playing": False})
    await amp._run_callback('playback_started', {"playing": True})
    await amp._run_callback('playback_completed', {"playing": False})
    
    # Verify all callbacks were called
    assert status_change_called
    assert playback_started_called
    assert playback_completed_called


@pytest.mark.asyncio
async def test_start_monitoring_compatibility():
    amp = AudioAmplifier(data_pin=25)
    
    # Create a callback to track status updates
    received_status = None
    
    async def test_callback(status):
        nonlocal received_status
        received_status = status
    
    # Test backward compatibility function
    await amp.start_monitoring(test_callback)
    
    # Verify the callback was registered
    assert amp._callbacks['status_change'] is test_callback
    assert amp._running == True
    
    # Call the _run_callback method to verify it works
    status = {"playing": False}
    await amp._run_callback('status_change', status)
    
    # Verify callback was called
    assert received_status == status
    
    # Clean up
    amp.stop()
    assert amp._running == False


@pytest.mark.asyncio
async def test_playback_loop_completion():
    amp = AudioAmplifier(data_pin=25, sample_rate=8000)
    
    # Create very short audio data (to test completion)
    audio_data = bytes([128, 200, 150, 100])
    amp._current_audio_data = audio_data
    amp._current_sample_idx = 0
    amp._playing = True
    
    # Start playback loop directly
    playback_task = asyncio.create_task(amp._playback_loop())
    
    # Allow some time for playback to complete
    await asyncio.sleep(0.5)
    
    # Check that playback completed
    assert amp._playing == False
    
    # Clean up
    await playback_task
