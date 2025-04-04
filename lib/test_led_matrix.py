import pytest
import uasyncio
from lib.led_matrix import LedMatrix, ANIMATION_STATES
from lib.shift_register import ShiftRegisterLed
from unittest.mock import AsyncMock, patch

def test_matrix_initialization(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    assert matrix.rows == 2
    assert matrix.cols == 2
    assert len(matrix.matrix) == 2
    assert len(matrix.matrix[0]) == 2
    assert matrix.is_powered
    assert matrix.current_animation == 'left-to-right'
    
def test_matrix_with_shift_register_tuples(mock_shift_register):
    pin_matrix = [[(mock_shift_register, 0), (mock_shift_register, 1)]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_pixel(0, 0, True)
    assert mock_shift_register.pins[0] == True
    matrix.set_pixel(0, 1, True)
    assert mock_shift_register.pins[1] == True

def test_set_pixel(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_pixel(0, 0, True)
    assert matrix.matrix[0][0].value() == 1
    
    matrix.set_pixel(0, 0, False)
    assert matrix.matrix[0][0].value() == 0

def test_clear_and_fill(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.fill()
    for row in matrix.matrix:
        for led in row:
            assert led.value() == 1
            
    matrix.clear()
    for row in matrix.matrix:
        for led in row:
            assert led.value() == 0

def test_set_row(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_row(0, [True, False])
    assert matrix.matrix[0][0].value() == 1
    assert matrix.matrix[0][1].value() == 0

def test_set_column(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_column(0, [True, False])
    assert matrix.matrix[0][0].value() == 1
    assert matrix.matrix[1][0].value() == 0

def test_animation_delay(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_animation_delay(1000)
    assert matrix.animation_delay == 1000

@pytest.mark.asyncio
async def test_animation_start_stop(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    step_fn = matrix.animate_left_to_right()
    assert callable(step_fn)
    assert matrix._running is False
    
    matrix.stop_animation()
    assert matrix._running is False

def test_power_toggle(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    assert matrix.is_powered  # On by default
    
    matrix.toggle_power()
    assert not matrix.is_powered
    for row in matrix.matrix:
        for led in row:
            assert led.value() == 0
            
    matrix.toggle_power()
    assert matrix.is_powered

def test_cycle_animation(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    assert matrix.current_animation == 'left-to-right'
    
    expected_sequence = ['sequential', 'ping-pong', 'binary', 'blink', 'left-to-right']
    seen_animations = []
    
    for expected in expected_sequence:
        matrix.cycle_animation()
        seen_animations.append(matrix.current_animation)
        assert matrix.current_animation == expected
        
    assert set(seen_animations) == set(ANIMATION_STATES)

def test_animation_disabled_when_powered_off(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.toggle_power()  # Turn off
    assert not matrix.is_powered
    
    matrix.cycle_animation()
    for row in matrix.matrix:
        for led in row:
            assert led.value() == 0

@pytest.mark.asyncio
async def test_all_animation_methods(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    matrix = LedMatrix(pin_matrix)
    
    original_sleep = uasyncio.sleep
    uasyncio.sleep = AsyncMock()
    
    try:
        animations = [
            (matrix.animate_blink_all, 'blink'),
            (matrix.animate_left_to_right, 'left-to-right'),
            (matrix.animate_sequential, 'sequential'),
            (matrix.animate_ping_pong, 'ping-pong'),
            (matrix.animate_binary_counter, 'binary')
        ]
        
        for animate, name in animations:
            step_fn = animate()
            assert callable(step_fn)
            await step_fn()  # Test one step of each animation
            matrix.stop_animation()
    finally:
        uasyncio.sleep = original_sleep

@pytest.mark.asyncio
async def test_monitor(mock_pin):
    pin_matrix = [[mock_pin(0), mock_pin(1)], [mock_pin(2), mock_pin(3)]]
    
    original_sleep = uasyncio.sleep
    uasyncio.sleep = AsyncMock()
    
    try:
        matrix = LedMatrix(pin_matrix)
        
        matrix._running = True
        matrix._animation_step = matrix.animate_left_to_right()
        
        await matrix._animation_step()
        assert matrix._running
        assert matrix.is_powered
        
        await matrix._animation_step()
        assert matrix._running
        
        matrix.stop_animation()
        assert not matrix._running
    except Exception as e:
        pytest.fail(f"Test failed with: {e}")
    finally:
        uasyncio.sleep = original_sleep
