from machine import Pin
from lib.led import Led
from lib.shift_register import ShiftRegisterLed
import uasyncio

ANIMATION_STATES = ['blink', 'left-to-right', 'sequential', 'ping-pong', 'binary', 
                   'radar', 'snake', 'random', 'star', 'pulse']

class LedMatrix:
    def __init__(self, pin_matrix, active_high=True, current_animation='left-to-right'):
        
        self.rows = len(pin_matrix)
        self.cols = len(pin_matrix[0])
        self._running = False
        self.matrix = []
        self.animation_delay = 300  # Increased from 100ms to 300ms for more visible blink pattern
        self.is_powered = True
        
        # Validate and set the animation
        if current_animation not in ANIMATION_STATES:
            print(f"Warning: Invalid animation '{current_animation}'. Using default 'blink'.")
            self.current_animation = 'blink'
        else:
            self.current_animation = current_animation
            
        print(f"Initializing with animation: {self.current_animation}")
        
        for row in pin_matrix:
            led_row = []
            for pin in row:
                if hasattr(pin, 'on') and hasattr(pin, 'off') and hasattr(pin, 'toggle'):
                    # Pin already has LED-like interface, use it directly
                    led_row.append(pin)
                elif isinstance(pin, tuple) and len(pin) == 2:
                    # Pin is a tuple with (shift_register, position)
                    shift_register, position = pin
                    if hasattr(shift_register, 'set_pin'):
                        # Pass the active_low parameter that could override the shift register's default
                        # active_low is the inverse of active_high
                        led_row.append(ShiftRegisterLed(shift_register, position, active_low=not active_high))
                    else:
                        raise ValueError(f"Invalid shift register pin: {pin}")
                else:
                    # No longer accepting raw pin numbers
                    raise ValueError(f"Invalid pin type: {pin}. Must provide either an LED object with on/off/toggle methods or a (shift_register, position) tuple.")
            self.matrix.append(led_row)
    
    def set_pixel(self, row, col, value):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if value:
                self.matrix[row][col].on()
            else:
                self.matrix[row][col].off()
    
    def _set_leds_synced(self, led_states):
        """
        Set multiple LEDs at once with proper synchronization between
        shift register LEDs and direct LEDs.
        
        Args:
            led_states: List of tuples in the format [(led, state), ...] where
                        state is True for on and False for off
        """
        # Organize LEDs into shift register LEDs and direct LEDs
        shift_registers = set()
        sr_led_states = []
        direct_led_states = []
        
        for led, state in led_states:
            if hasattr(led, 'shift_register'):
                shift_registers.add(led.shift_register)
                sr_led_states.append((led, state))
            else:
                direct_led_states.append((led, state))
        
        # Begin batch mode on all shift registers
        for sr in shift_registers:
            sr.begin_batch()
            
        # First update all shift register LEDs
        for led, state in sr_led_states:
            if state:
                led.on()
            else:
                led.off()
                
        # End batch mode on all shift registers
        for sr in shift_registers:
            sr.end_batch()
            
        # Now update all direct pin LEDs after shift registers have updated
        for led, state in direct_led_states:
            if state:
                led.on()
            else:
                led.off()
    
    def _set_matrix_pattern(self, pattern_func):
        """
        Set a pattern across the entire matrix. The pattern_func will be called
        for each LED position to determine if it should be on or off.
        
        Args:
            pattern_func: Function that takes (row, col) and returns True (on) or False (off)
        """
        # Build a list of all LEDs and their desired states
        led_states = []
        
        for row in range(self.rows):
            for col in range(self.cols):
                led = self.matrix[row][col]
                state = pattern_func(row, col)
                led_states.append((led, state))
                
        # Set all LEDs with proper synchronization
        self._set_leds_synced(led_states)
    
    def clear(self):
        """Turn off all LEDs in the matrix"""
        # Simply use _set_matrix_pattern with a function that always returns False
        self._set_matrix_pattern(lambda row, col: False)
    
    def fill(self):
        """Turn on all LEDs in the matrix"""
        # Simply use _set_matrix_pattern with a function that always returns True
        self._set_matrix_pattern(lambda row, col: True)
    
    def toggle_pixel(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.matrix[row][col].toggle()
    
    def set_row(self, row, values):
        if 0 <= row < self.rows and len(values) == self.cols:
            # Create a list of LEDs and their states
            led_states = []
            for col, value in enumerate(values):
                led = self.matrix[row][col]
                led_states.append((led, value))
            
            # Update all LEDs in the row synchronously
            self._set_leds_synced(led_states)
    
    def set_column(self, col, values):
        if 0 <= col < self.cols and len(values) == self.rows:
            # Create a list of LEDs and their states
            led_states = []
            for row, value in enumerate(values):
                led = self.matrix[row][col]
                led_states.append((led, value))
            
            # Update all LEDs in the column synchronously
            self._set_leds_synced(led_states)
    
    def set_animation_delay(self, ms):
        self.animation_delay = ms
        
    def stop_animation(self):
        self._running = False
        
    def animate_left_to_right(self):
        current_col = 0
        
        async def animation_step():
            nonlocal current_col
            
            # Define a pattern function that only lights up LEDs in the current column
            def pattern(row, col):
                return col == current_col
                
            # Apply the pattern to the entire matrix
            self._set_matrix_pattern(pattern)
                
            # Move to the next column
            current_col = (current_col + 1) % self.cols
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step
        
    def animate_blink_all(self):
        """
        Simple blink animation: all LEDs turn on and off together.
        """
        state = False
        
        async def animation_step():
            nonlocal state
            print(f"Blink animation: {'OFF' if state else 'ON'}")
            if state:
                # Turn all LEDs off
                self.clear()
            else:
                # Turn all LEDs on
                self.fill()
            state = not state
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step
        
    def animate_sequential(self):
        """
        Light up one LED at a time in sequence, moving through the entire matrix
        row by row, from left to right.
        """
        current_row = 0
        current_col = 0
        
        async def animation_step():
            nonlocal current_row, current_col
            
            # Define a pattern function that only lights up the current LED
            def pattern(row, col):
                return row == current_row and col == current_col
                
            # Apply the pattern to the entire matrix
            self._set_matrix_pattern(pattern)
            
            # Move to the next position
            current_col += 1
            if current_col >= self.cols:
                current_col = 0
                current_row += 1
                if current_row >= self.rows:
                    current_row = 0
            
            await uasyncio.sleep(self.animation_delay/1000)
                    
        return animation_step
        
    def animate_ping_pong(self):
        """
        Move a dot back and forth across the matrix.
        Uses all rows by creating a cascading effect.
        """
        current_col = 0
        direction = 1  # 1 for right, -1 for left
        
        async def animation_step():
            nonlocal current_col, direction
            
            # Define a pattern function that creates the cascading effect
            def pattern(row, col):
                pos = (current_col + row) % self.cols
                return col == pos
                
            # Apply the pattern to the entire matrix
            self._set_matrix_pattern(pattern)
            
            # Change direction when reaching the edge
            if current_col >= self.cols - 1:
                direction = -1
            elif current_col <= 0:
                direction = 1
                
            current_col += direction
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step
        
    def animate_binary_counter(self):
        """
        Display binary numbers on the matrix.
        Each column represents a bit, and each row can display a different number.
        """
        current_number = 0
        
        async def animation_step():
            nonlocal current_number
            
            # Define a pattern function that creates binary counting patterns
            def pattern(row, col):
                # Each row shows a different number in sequence
                row_number = (current_number + row) % (2 ** self.cols)
                binary = '{:0{}b}'.format(row_number, self.cols)
                
                # Check if this position should be on based on binary representation
                if col < len(binary):
                    # Align binary pattern to the right
                    col_pos = self.cols - len(binary) + col
                    if col_pos >= 0:
                        return binary[col] == '1'
                return False
            
            # Apply the pattern to the entire matrix
            self._set_matrix_pattern(pattern)
            
            current_number = (current_number + 1) % (2 ** self.cols)
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step
    
    def animate_radar(self):
        """
        Create a radar-like sweeping animation, ideal for pentagon LED layout.
        Single LED moves around the pentagon perimeter.
        """
        current_pos = 0
        
        async def animation_step():
            nonlocal current_pos
            
            # For a pentagon, we want to light LEDs in a circular pattern
            def pattern(row, col):
                # Calculate total position in matrix
                pos = row * self.cols + col
                # Return True only for the current radar position
                return pos == current_pos
            
            self._set_matrix_pattern(pattern)
            
            # Move to next position in pentagon pattern
            current_pos = (current_pos + 1) % (self.rows * self.cols)
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step
    
    def animate_snake(self):
        """
        Create a snake-like animation moving around the pentagon.
        Three LEDs lit in sequence, following each other.
        """
        head_pos = 0
        
        async def animation_step():
            nonlocal head_pos
            
            # Define pattern that lights up 3 consecutive positions
            def pattern(row, col):
                pos = row * self.cols + col
                total_leds = self.rows * self.cols
                # Light up head and two trailing positions
                return (pos == head_pos or 
                       pos == ((head_pos - 1) % total_leds) or 
                       pos == ((head_pos - 2) % total_leds))
            
            self._set_matrix_pattern(pattern)
            
            # Move snake head forward
            head_pos = (head_pos + 1) % (self.rows * self.cols)
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step
    
    def animate_random(self):
        """
        Create symmetric random patterns suitable for pentagon layout.
        """
        import random
        pattern_duration = 0
        current_pattern = {}
        
        async def animation_step():
            nonlocal pattern_duration, current_pattern
            
            if pattern_duration <= 0:
                # Generate new symmetric pattern
                current_pattern = {(row, col): random.choice([True, False])
                                 for row in range(self.rows)
                                 for col in range(self.cols)}
                pattern_duration = 3  # Keep pattern for 3 steps
            
            pattern_duration -= 1
            self._set_matrix_pattern(lambda r, c: current_pattern[(r, c)])
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step

    def animate_star(self):
        """
        Create a star pattern effect by alternating between inner and outer LEDs.
        """
        state = False
        
        async def animation_step():
            nonlocal state
            
            def pattern(row, col):
                # For pentagon layout, alternate between outer and inner positions
                pos = row * self.cols + col
                total_leds = self.rows * self.cols
                is_outer = pos % 2 == 0  # Every other LED is on the outer edge
                return is_outer if state else not is_outer
            
            self._set_matrix_pattern(pattern)
            state = not state
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step

    def animate_pulse(self):
        """
        Create a breathing/pulsing effect using patterns.
        """
        phase = 0
        max_phases = 8  # Number of different patterns to create pulsing effect
        
        async def animation_step():
            nonlocal phase
            
            def pattern(row, col):
                # Calculate LED position in pentagon
                pos = row * self.cols + col
                total_leds = self.rows * self.cols
                
                # Create pulsing pattern based on current phase
                if phase < max_phases // 2:
                    # Expanding phase
                    return pos < (phase + 1)
                else:
                    # Contracting phase
                    return pos < (max_phases - phase)
            
            self._set_matrix_pattern(pattern)
            phase = (phase + 1) % max_phases
            await uasyncio.sleep(self.animation_delay/1000)
            
        return animation_step
        
    def toggle_power(self):
        self.is_powered = not self.is_powered
        print(f"Power toggled: {'on' if self.is_powered else 'off'}")
        
        if not self.is_powered:
            self.stop_animation()
            self.clear()
        else:
            self.cycle_animation()
            
    def cycle_animation(self):
        if not self.is_powered:
            return
        
        # Make sure we're finding the correct index in ANIMATION_STATES
        try:
            current_idx = ANIMATION_STATES.index(self.current_animation)
        except ValueError:
            # In case of any issue, restart with blink
            print(f"Warning: Animation '{self.current_animation}' not in ANIMATION_STATES. Resetting to 'blink'.")
            self.current_animation = 'blink'
            current_idx = ANIMATION_STATES.index('blink')
            
        # Move to the next animation in the sequence
        self.current_animation = ANIMATION_STATES[(current_idx + 1) % len(ANIMATION_STATES)]
        print(f"Animation changed to: {self.current_animation}")
        
        # Stop current animation and set up the new one
        self.stop_animation()
        
        # Set the appropriate animation function
        self._set_animation_function()
        self._running = True
        
    def _set_animation_function(self):
        """Helper method to set the correct animation function based on current_animation"""
        if self.current_animation == 'blink':
            self._animation_step = self.animate_blink_all()
        elif self.current_animation == 'left-to-right':
            self._animation_step = self.animate_left_to_right()
        elif self.current_animation == 'sequential':
            self._animation_step = self.animate_sequential()
        elif self.current_animation == 'ping-pong':
            self._animation_step = self.animate_ping_pong()
        elif self.current_animation == 'binary':
            self._animation_step = self.animate_binary_counter()
        elif self.current_animation == 'radar':
            self._animation_step = self.animate_radar()
        elif self.current_animation == 'snake':
            self._animation_step = self.animate_snake()
        elif self.current_animation == 'random':
            self._animation_step = self.animate_random()
        elif self.current_animation == 'star':
            self._animation_step = self.animate_star()
        elif self.current_animation == 'pulse':
            self._animation_step = self.animate_pulse()
        else:
            # Default to blink if animation not recognized
            print(f"Warning: Unknown animation '{self.current_animation}'. Using 'blink'.")
            self.current_animation = 'blink'
            self._animation_step = self.animate_blink_all()
            
    async def monitor(self):
        """
        Start the animation monitoring loop using the current animation setting.
        """
        self._running = True
        
        # Start with the currently selected animation
        print(f"Starting monitor with animation: {self.current_animation}")
        
        # Use our helper function to set up the animation
        self._set_animation_function()
        
        while self._running:
            try: 
                if self.is_powered:
                    await self._animation_step()
                else:
                    await uasyncio.sleep(0.1)
                await uasyncio.sleep(0)  # Allow other tasks to run
            except Exception as e:
                print(f"Animation error: {e}")
                break
            
        self._running = False
