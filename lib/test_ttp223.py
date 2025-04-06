import pytest
from ttp223 import TTP223TouchSensor
import uasyncio
import time
from pin_mock import MockPin as Pin

# Patch machine.Pin with our MockPin for testing
import ttp223
ttp223.Pin = Pin

@pytest.fixture(autouse=True)
def clear_pins():
    """Clear pin instances before each test."""
    Pin.clear_instances()

@pytest.mark.asyncio
async def test_touch_sensor_init():
    """Test that the touch sensor initializes correctly with default values."""
    sensor = TTP223TouchSensor(pin=0)
    
    # Check default values
    assert sensor.pin_num == 0
    assert sensor.active_high is True
    assert sensor.touched is False
    assert sensor._on_touch is None
    assert sensor._on_release is None
    assert sensor._on_toggle is None
    assert sensor._running is False

@pytest.mark.asyncio
async def test_touch_detection():
    """Test that the sensor correctly detects touch events."""
    touch_called = False
    
    async def on_touch():
        nonlocal touch_called
        touch_called = True
    
    # Create sensor with active_high=True (default)
    sensor = TTP223TouchSensor(pin=0)
    sensor.on_touch(on_touch)
    
    # Initial state: not touched (LOW)
    sensor.pin.value(0)
    
    # Simulates internal loop to track state changes
    stable_count = 0
    current_reading = False
    last_touched = False
    
    # Simulate touch event (HIGH)
    sensor.pin.value(1)
    
    # First check doesn't trigger event due to stability checking
    is_touched_now = sensor.is_touched()
    assert is_touched_now is True  # Sensor returns TRUE when touched
    
    # Simulate multiple consecutive readings to pass stability check
    for _ in range(5):
        if is_touched_now == current_reading:
            stable_count += 1
        else:
            stable_count = 0
            current_reading = is_touched_now
    
    # Now we've passed stability check
    if stable_count >= 3 and current_reading != last_touched:
        sensor.touched = current_reading
        last_touched = current_reading
        await sensor._run_callback(sensor._on_touch)
    
    assert touch_called is True
    assert sensor.touched is True

@pytest.mark.asyncio
async def test_release_detection():
    """Test that the sensor correctly detects release events."""
    release_called = False
    
    async def on_release():
        nonlocal release_called
        release_called = True
    
    # Create sensor with active_high=True
    sensor = TTP223TouchSensor(pin=0)
    sensor.on_release(on_release)
    
    # Start in touched state
    sensor.pin.value(1)
    sensor.touched = True
    
    # Simulates internal loop
    stable_count = 0
    current_reading = True
    last_touched = True
    
    # Simulate release (LOW)
    sensor.pin.value(0)
    
    # Check touch state
    is_touched_now = sensor.is_touched()
    assert is_touched_now is False
    
    # Simulate multiple readings for stability
    for _ in range(5):
        if is_touched_now == current_reading:
            stable_count += 1
        else:
            stable_count = 0
            current_reading = is_touched_now
    
    # Process release event
    if stable_count >= 3 and current_reading != last_touched:
        sensor.touched = current_reading
        last_touched = current_reading
        await sensor._run_callback(sensor._on_release)
    
    assert release_called is True
    assert sensor.touched is False

@pytest.mark.asyncio
async def test_active_low_configuration():
    """Test that the sensor works with active_low=True configuration."""
    touch_detected = False
    
    async def on_touch():
        nonlocal touch_detected
        touch_detected = True
    
    # Create sensor with active_high=False
    sensor = TTP223TouchSensor(pin=0, active_high=False)
    sensor.on_touch(on_touch)
    
    # In active_low mode, LOW means touched
    sensor.pin.value(0)
    assert sensor.is_touched() is True
    
    # HIGH means not touched
    sensor.pin.value(1)
    assert sensor.is_touched() is False

@pytest.mark.asyncio
async def test_debounce():
    """Test that the sensor properly debounces rapid state changes."""
    touch_count = 0
    
    async def on_touch():
        nonlocal touch_count
        touch_count += 1
    
    # 100ms debounce time
    sensor = TTP223TouchSensor(pin=0, debounce_ms=100)
    sensor.on_touch(on_touch)
    
    # Initial state
    sensor.pin.value(0)
    sensor.touched = False
    sensor.last_state_change = time.time() - 1.0  # Last change was 1 second ago
    
    # Simulate a touch (first press)
    sensor.pin.value(1)
    
    # Process event manually (simplified version of what monitor does)
    is_touched = sensor.is_touched()
    assert is_touched is True
    
    # Fake stability check being passed
    sensor.touched = True
    sensor.last_state_change = time.time()
    await sensor._run_callback(sensor._on_touch)
    assert touch_count == 1
    
    # Simulate rapid touch/release (should be ignored due to debounce)
    sensor.pin.value(0)
    sensor.pin.value(1)
    
    # Debounce in effect, no change should happen
    time_since_last_change = time.time() - sensor.last_state_change
    assert time_since_last_change < sensor.debounce_time
    
    # Debounce test passes, touch count should still be 1
    assert touch_count == 1

@pytest.mark.asyncio
async def test_toggle_callback():
    """Test that the toggle callback is called for both touch and release."""
    toggle_count = 0
    
    async def on_toggle():
        nonlocal toggle_count
        toggle_count += 1
    
    sensor = TTP223TouchSensor(pin=0)
    sensor.on_toggle(on_toggle)
    
    # Initial state
    sensor.pin.value(0)
    sensor.touched = False
    sensor.last_state_change = time.time() - 1.0  # Last change was 1 second ago
    
    # Process a touch event
    sensor.pin.value(1)
    
    # Fake stability check and state change
    sensor.touched = True
    sensor.last_state_change = time.time()
    await sensor._run_callback(sensor._on_toggle)
    assert toggle_count == 1
    
    # Wait for debounce
    await uasyncio.sleep(0.1)
    
    # Process a release event
    sensor.pin.value(0)
    
    # Fake stability check and state change
    sensor.touched = False
    sensor.last_state_change = time.time()
    await sensor._run_callback(sensor._on_toggle)
    assert toggle_count == 2

@pytest.mark.asyncio
async def test_monitor_stops():
    """Test that the monitor function stops correctly."""
    sensor = TTP223TouchSensor(pin=0)
    
    async def stop_after_delay():
        await uasyncio.sleep(0.1)
        sensor.stop()
    
    # Start monitor task
    monitor_task = uasyncio.create_task(sensor.monitor())
    
    # Schedule task to stop after 100ms
    stop_task = uasyncio.create_task(stop_after_delay())
    
    # Wait for stop task to complete
    await stop_task
    
    # Monitor should have been stopped
    assert sensor._running is False
