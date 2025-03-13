from machine import Pin, Timer
from lib.led import Led
import time

class LedMatrix:
    def __init__(self, pin_matrix, active_low=False):
        self.rows = len(pin_matrix)
        self.cols = len(pin_matrix[0])
        self.matrix = []
        self.animation_timer = None
        self.animation_delay = 500
        
        for row in pin_matrix:
            led_row = []
            for pin in row:
                led_row.append(Led(pin, active_low))
            self.matrix.append(led_row)
    
    def set_pixel(self, row, col, value):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if value:
                self.matrix[row][col].on()
            else:
                self.matrix[row][col].off()
    
    def clear(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.matrix[row][col].off()
    
    def fill(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.matrix[row][col].on()
    
    def toggle_pixel(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.matrix[row][col].toggle()
    
    def set_row(self, row, values):
        if 0 <= row < self.rows and len(values) == self.cols:
            for col, value in enumerate(values):
                self.set_pixel(row, col, value)
    
    def set_column(self, col, values):
        if 0 <= col < self.cols and len(values) == self.rows:
            for row, value in enumerate(values):
                self.set_pixel(row, col, value)
    
    def _stop_current_animation(self):
        if self.animation_timer:
            self.animation_timer.deinit()
            self.animation_timer = None
            
    def set_animation_delay(self, ms):
        self.animation_delay = ms
        
    def stop_animation(self):
        self._stop_current_animation()
        self.clear()
        
    def animate_left_to_right(self):
        self._stop_current_animation()
        current_col = 0
        
        def animation_step(timer):
            nonlocal current_col
            self.clear()
            for row in range(self.rows):
                self.set_pixel(row, current_col, True)
            current_col = (current_col + 1) % self.cols
            
        self.animation_timer = Timer(-1)
        self.animation_timer.init(period=self.animation_delay, mode=Timer.PERIODIC, callback=animation_step)
        
    def animate_blink_all(self):
        self._stop_current_animation()
        state = False
        
        def animation_step(timer):
            nonlocal state
            if state:
                self.clear()
            else:
                self.fill()
            state = not state
            
        self.animation_timer = Timer(-1)
        self.animation_timer.init(period=self.animation_delay, mode=Timer.PERIODIC, callback=animation_step)