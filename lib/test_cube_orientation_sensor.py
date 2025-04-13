import pytest
from unittest.mock import MagicMock
from machine import I2C, Pin
from cube_orientation_sensor import CubeOrientationSensor, CubeSide

class TestCubeOrientationSensor:
    def setup_method(self):
        self.i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        self.i2c.writeto_mem = MagicMock()
        self.i2c.readfrom_mem = MagicMock()
        self.sensor = CubeOrientationSensor(self.i2c)
        
    def test_init_sensor(self):
        self.i2c.writeto_mem.assert_called_once_with(0x68, 0x6B, bytes([0]))
        
    def test_get_cube_side_top(self):
        self.i2c.readfrom_mem.side_effect = [
            bytes([0x00, 0x00]),  # x = 0
            bytes([0x00, 0x00]),  # y = 0
            bytes([0x40, 0x00]),  # z = 16384 (positive)
        ]
        assert self.sensor.get_cube_side() == CubeSide.TOP
        
    def test_get_cube_side_bottom(self):
        self.i2c.readfrom_mem.side_effect = [
            bytes([0x00, 0x00]),  # x = 0
            bytes([0x00, 0x00]),  # y = 0
            bytes([0xC0, 0x00]),  # z = -16384 (negative)
        ]
        assert self.sensor.get_cube_side() == CubeSide.BOTTOM
        
    def test_get_cube_side_right(self):
        self.i2c.readfrom_mem.side_effect = [
            bytes([0x40, 0x00]),  # x = 16384 (positive)
            bytes([0x00, 0x00]),  # y = 0
            bytes([0x00, 0x00]),  # z = 0
        ]
        assert self.sensor.get_cube_side() == CubeSide.RIGHT
        
    def test_get_cube_side_left(self):
        self.i2c.readfrom_mem.side_effect = [
            bytes([0xC0, 0x00]),  # x = -16384 (negative)
            bytes([0x00, 0x00]),  # y = 0
            bytes([0x00, 0x00]),  # z = 0
        ]
        assert self.sensor.get_cube_side() == CubeSide.LEFT
        
    def test_get_cube_side_front(self):
        self.i2c.readfrom_mem.side_effect = [
            bytes([0x00, 0x00]),  # x = 0
            bytes([0x40, 0x00]),  # y = 16384 (positive)
            bytes([0x00, 0x00]),  # z = 0
        ]
        assert self.sensor.get_cube_side() == CubeSide.FRONT
        
    def test_get_cube_side_back(self):
        self.i2c.readfrom_mem.side_effect = [
            bytes([0x00, 0x00]),  # x = 0
            bytes([0xC0, 0x00]),  # y = -16384 (negative)
            bytes([0x00, 0x00]),  # z = 0
        ]
        assert self.sensor.get_cube_side() == CubeSide.BACK
