from lib.shift_register import ShiftRegister
import pytest

def test_daisy_chain_initialization(mock_pin):
    sr = ShiftRegister(10, 11, 12, registers=2)
    assert sr.registers == 2
    assert sr.position == 0
    assert len(sr.state) == 2
    assert all(x == 0 for x in sr.state)

def test_next_register(mock_pin):
    sr = ShiftRegister(10, 11, 12, registers=2)
    next_sr = sr.next()
    assert next_sr.position == 1
    assert next_sr.registers == 2
    assert next_sr.state == sr.state  # They share the same state array

def test_next_register_overflow(mock_pin):
    sr = ShiftRegister(10, 11, 12, registers=1)
    with pytest.raises(ValueError, match="No more registers in chain"):
        sr.next()

def test_set_pin_in_chain(mock_pin):
    sr = ShiftRegister(10, 11, 12, registers=2)
    next_sr = sr.next()
    
    sr.set_pin(0, True)      # Set pin in first register
    next_sr.set_pin(7, True) # Set pin in second register
    
    assert sr.state[0] == 0x01    # First register, first pin
    assert sr.state[1] == 0x80    # Second register, last pin
