import random

import uasyncio

from lib.auto_shutdown import AutoShutdown
from lib.button import DebouncedButton
from lib.led_matrix import ANIMATION_STATES, LedMatrix
from lib.pin_config import PinConfigEsp32C3
from lib.shift_register import ShiftRegister


class CubeLedPinConfig(PinConfigEsp32C3):
    """ESP32-C3 pin configuration for cube LED animation"""
    @property
    def shift_register_pins(self):
        return {
            'ser': 0,  # Serial data
            'rclk': 1,  # Register clock
            'srclk': 2,  # Shift register clock
        }


async def main():
    try:
        pin_config = CubeLedPinConfig()
        auto_shutdown = AutoShutdown(timeout=600)  # 600 seconds = 10 minutes

        pins = pin_config.shift_register_pins
        shift_register = ShiftRegister(ser=pins['ser'], rclk=pins['rclk'], srclk=pins['srclk'])

        led_matrix = LedMatrix(
            [
                [
                    shift_register.q0,
                    shift_register.q7,
                    shift_register.q5,
                    shift_register.q4,
                    shift_register.q2,
                ]
            ],
            active_high=True,
            current_animation=random.choice(ANIMATION_STATES),
        )

        board_button = DebouncedButton(pin_config.BOOT_BUTTON)

        async def cycle_animation():
            print('Cycling animation')
            led_matrix.cycle_animation()

        # Board button toggles power on/off
        board_button.on_press(cycle_animation)

        await uasyncio.gather(
            led_matrix.monitor(),
            board_button.monitor(),
            auto_shutdown.monitor(),
        )
    except KeyboardInterrupt:
        print('Keyboard interrupt received')
        try:
            board_button.stop()
            auto_shutdown.stop()
            led_matrix.stop_animation()
        except Exception as e:
            print('Error during cleanup:', str(e))
    except Exception as e:
        print('Error in main:', str(e))
        raise


if __name__ == '__main__':
    print('Initializing system...')
    uasyncio.run(main())
