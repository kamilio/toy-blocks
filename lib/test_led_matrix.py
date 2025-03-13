import pytest
from lib.led_matrix import LedMatrix

def test_matrix_initialization():
    pin_matrix = [[0, 1], [2, 3]]
    matrix = LedMatrix(pin_matrix)
    assert matrix.rows == 2
    assert matrix.cols == 2
    assert len(matrix.matrix) == 2
    assert len(matrix.matrix[0]) == 2

def test_set_pixel():
    pin_matrix = [[0, 1], [2, 3]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_pixel(0, 0, True)
    assert matrix.matrix[0][0].led.value() == 1
    
    matrix.set_pixel(0, 0, False)
    assert matrix.matrix[0][0].led.value() == 0

def test_clear_and_fill():
    pin_matrix = [[0, 1], [2, 3]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.fill()
    for row in matrix.matrix:
        for led in row:
            assert led.led.value() == 1
            
    matrix.clear()
    for row in matrix.matrix:
        for led in row:
            assert led.led.value() == 0

def test_set_row():
    pin_matrix = [[0, 1], [2, 3]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_row(0, [True, False])
    assert matrix.matrix[0][0].led.value() == 1
    assert matrix.matrix[0][1].led.value() == 0

def test_set_column():
    pin_matrix = [[0, 1], [2, 3]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_column(0, [True, False])
    assert matrix.matrix[0][0].led.value() == 1
    assert matrix.matrix[1][0].led.value() == 0

def test_animation_delay():
    pin_matrix = [[0, 1], [2, 3]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.set_animation_delay(1000)
    assert matrix.animation_delay == 1000

def test_animation_start_stop():
    pin_matrix = [[0, 1], [2, 3]]
    matrix = LedMatrix(pin_matrix)
    
    matrix.animate_left_to_right()
    assert matrix.animation_timer is not None
    
    matrix.stop_animation()
    assert matrix.animation_timer is None
    for row in matrix.matrix:
        for led in row:
            assert led.led.value() == 0