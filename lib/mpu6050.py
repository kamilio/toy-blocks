from micropython import const
from machine import I2C, Pin
from enum import Enum

class CubeSide(Enum):
    TOP = const("top")
    BOTTOM = const("bottom")
    RIGHT = const("right")
    LEFT = const("left")
    FRONT = const("front")
    BACK = const("back")

class MPU6050:
    PWR_MGMT_1 = const(0x6B)
    ACCEL_XOUT_H = const(0x3B)
    ACCEL_YOUT_H = const(0x3D)
    ACCEL_ZOUT_H = const(0x3F)
    
    def __init__(self, i2c, addr=const(0x68)):
        self.i2c = i2c
        self.addr = addr
        self.init_sensor()
    
    def init_sensor(self):
        self.i2c.writeto_mem(self.addr, self.PWR_MGMT_1, bytes([0]))
    
    def _read_raw_accel(self):
        x = self.i2c.readfrom_mem(self.addr, self.ACCEL_XOUT_H, 2)
        y = self.i2c.readfrom_mem(self.addr, self.ACCEL_YOUT_H, 2)
        z = self.i2c.readfrom_mem(self.addr, self.ACCEL_ZOUT_H, 2)
        
        x_val = int.from_bytes(x, 'big')
        y_val = int.from_bytes(y, 'big')
        z_val = int.from_bytes(z, 'big')
        
        if x_val > 0x7FFF:
            x_val -= 0x10000
        if y_val > 0x7FFF:
            y_val -= 0x10000
        if z_val > 0x7FFF:
            z_val -= 0x10000
            
        return x_val, y_val, z_val
    
    def get_cube_side(self) -> CubeSide:
        x, y, z = self._read_raw_accel()
        
        abs_values = [abs(x), abs(y), abs(z)]
        max_index = abs_values.index(max(abs_values))
        
        if max_index == 0:  # X-axis
            return CubeSide.RIGHT if x > 0 else CubeSide.LEFT
        elif max_index == 1:  # Y-axis
            return CubeSide.FRONT if y > 0 else CubeSide.BACK
        else:  # Z-axis
            return CubeSide.TOP if z > 0 else CubeSide.BOTTOM