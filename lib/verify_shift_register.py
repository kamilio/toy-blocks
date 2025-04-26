"""
Test script specifically to diagnose why the fill() method isn't turning on all LEDs.
This tries several different approaches to turning on all LEDs.
"""

import time
from shift_register import ShiftRegister


async def verify_shift_register(pin_config):
    print('=== Shift Register All-On Test ===')

    # Initialize shift register using provided pin configuration
    pins = pin_config.shift_register_pins

    print(
        f"Creating shift register with pins: "
        f"SER={pins['ser']}, RCLK={pins['rclk']}, SRCLK={pins['srclk']}"
    )
    sr = ShiftRegister(ser=pins['ser'], rclk=pins['rclk'], srclk=pins['srclk'])

    print('\nMethod 1: Using fill()')
    sr.fill()
    print('Fill completed - check if all LEDs are on')
    time.sleep(5)  # Wait for observation

    print('\nMethod 2: Manually set each pin HIGH')
    for i in range(8):
        sr.set_pin(i, True)
        time.sleep(0.1)  # Small delay between each pin
    print('All pins set HIGH - check if all LEDs are on')
    time.sleep(5)

    print('\nMethod 3: Direct bit manipulation')
    # Set all bits directly
    sr.state[0] = 0xFF
    sr.update()
    print('All bits set to 1 directly - check if all LEDs are on')
    time.sleep(5)

    print('\nMethod 4: Raw pin manipulation')
    # Try directly manipulating pins
    sr.clear()  # Start with a clean state

    # Send 8 bits of 1
    for _ in range(8):
        sr.ser_pin.value(1)  # Data bit = 1

        # Pulse the shift register clock
        sr.srclk_pin.value(0)
        time.sleep(0.000005)
        sr.srclk_pin.value(1)
        time.sleep(0.000005)
        sr.srclk_pin.value(0)
        time.sleep(0.000005)

    # Pulse the storage register clock to latch data
    sr.rclk_pin.value(0)
    time.sleep(0.000005)
    sr.rclk_pin.value(1)
    time.sleep(0.000005)
    sr.rclk_pin.value(0)

    print('Raw pin manipulation complete - check if all LEDs are on')
    time.sleep(5)

    print('\nMethod 5: Inverse logic - setting all bits to 0')
    sr.state[0] = 0x00  # All LOW
    sr.update()
    print('All bits set to 0 directly - check if all LEDs are on (if active low)')
    time.sleep(5)

    print('\nTest complete! Did any method work?')
