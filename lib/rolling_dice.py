from machine import Pin, Timer
from lib.led import Led
import random

class RollingDice:
    # LED Layout Reference:
    #    TL    TR    [0,1]
    #     MID       [2]
    #    BL    BR    [3,4]
    #    LL    LR    [5,6]
    DICE_PATTERNS = {
        1: [0, 0, 1, 0, 0, 0, 0],  # Center only
        2: [0, 0, 0, 1, 1, 0, 0],  # Bottom left, Bottom right
        3: [0, 1, 1, 0, 0, 1, 0],  # Top right, Middle, Lower left
        4: [1, 1, 0, 0, 0, 1, 1],  # TL, TR, LL, LR
        5: [1, 1, 1, 0, 0, 1, 1],  # Like 4 + Middle
        6: [1, 1, 0, 1, 1, 1, 1]   # All except center
    }

    def __init__(self, pins, active_low=False):
        if len(pins) != 7:
            raise ValueError("Exactly 7 pins required for dice display")
        
        self.pins = pins    
        self.leds = []
        # Handle both direct pins and shift register virtual pins
        for pin in pins:
            if isinstance(pin, tuple) and len(pin) == 2:
                shift_register, position = pin
                self.leds.append(Led(pin, active_low))
            else:
                self.leds.append(Led(pin, active_low))
                
        self.animation_timer = None
        self.animation_delay = 80
        self.current_number = None
        self.animation_count = 0
        self.ANIMATION_STEPS = 30
        
    def clear(self):
        for led in self.leds:
            led.off()
            if hasattr(led.led, 'shift_register'):
                led.led.shift_register.write()
            
    def test(self):
        for led in self.leds:
            led.on()
            if hasattr(led.led, 'shift_register'):
                led.led.shift_register.write()
                
    def cycle_number(self):
        if self.current_number is None:
            self.test()  # Show all LEDs
            self.current_number = 0
        else:
            next_number = (self.current_number % 6) + 1
            if next_number == 1 and self.current_number != 0:
                self.test()  # Show all LEDs after 6
                self.current_number = 0
            else:
                self.display_number(next_number)
                self.current_number = next_number
    
    def display_number(self, number):
        if number not in self.DICE_PATTERNS:
            return
        self.current_number = number
        
        pattern = self.DICE_PATTERNS[number]
        shift_register = None
        
        for led, value in zip(self.leds, pattern):
            if value:
                led.on()
            else:
                led.off()
            if hasattr(led.led, 'shift_register'):
                shift_register = led.led.shift_register
                
        if shift_register:
            shift_register.write()
    
    def _stop_animation(self):
        if self.animation_timer:
            self.animation_timer.deinit()
            self.animation_timer = None
    
    def roll(self):
        self._stop_animation()
        self.animation_count = 0
        animation_position = 0
        final_number = random.randint(1, 6)
        
        def animation_step(timer):
            nonlocal animation_position            
            if self.animation_count < self.ANIMATION_STEPS:
                self.clear()
                # Single dot circling: TL -> TR -> BR -> LR -> LL -> BL
                edge_leds = [0, 1, 4, 6, 5, 3]  # TL, TR, BR, LR, LL, BL
                curr_pos = animation_position % len(edge_leds)
                
                self.leds[edge_leds[curr_pos]].on()  # Light only current LED
                for led in self.leds:
                    if hasattr(led.led, 'shift_register'):
                        led.led.shift_register.write()
                animation_position += 1
                self.animation_count += 1
            else:
                self.display_number(final_number)
                self.current_number = final_number
                self._stop_animation()
        
        self.animation_timer = Timer(-1)
        self.animation_timer.init(period=self.animation_delay, mode=Timer.PERIODIC, callback=animation_step)

    def debug_display(self):
        print("\nDice LED Pin Layout:\n")
        print("   {}     {}".format(
            self._format_pin(self.pins[0]), 
            self._format_pin(self.pins[1])
        ))
        print("   (TL)   (TR)\n")
        print("      {}".format(self._format_pin(self.pins[2])))
        print("    (MID)\n")
        print("   {}     {}".format(
            self._format_pin(self.pins[3]), 
            self._format_pin(self.pins[4])
        ))
        print("   (BL)   (BR)\n")
        print("   {}     {}".format(
            self._format_pin(self.pins[5]), 
            self._format_pin(self.pins[6])
        ))
        print("   (LL)   (LR)")

    def _format_pin(self, pin):
        if isinstance(pin, tuple) and len(pin) == 2:
            shift_register, position = pin
            return f"(sr_0,{position})"
        return str(pin)
