import uasyncio
import random
from lib.button import Button
from lib.auto_shutdown import AutoShutdown
from lib.board_button import BoardButton
from lib.board_config import BoardConfig
from lib.led_matrix import LedMatrix, ANIMATION_STATES
from lib.shift_register import ShiftRegister, ShiftRegisterLed
from lib.led import Led


async def main():
    try:
        board_config = BoardConfig(detected_board="ESP32-C3")
        auto_shutdown = AutoShutdown(timeout=600) # 600 seconds = 10 minutes

        pins = board_config.shift_register_pins
        shift_register = ShiftRegister(
            ser=pins['ser'],
            rclk=pins['rclk'],
            srclk=pins['srclk']
        )
        
        led_matrix = LedMatrix([[
                shift_register.q0,
                shift_register.q7,
                shift_register.q5,
                shift_register.q4,
                shift_register.q2,
            ]], 
            active_high=True, 
            current_animation=random.choice(ANIMATION_STATES)
        )

        board_button = BoardButton(board_config)
        async def cycle_animation():
            print("Cycling animation")
            led_matrix.cycle_animation()


        button = Button(pin=board_config.custom_button_pin)
        # Board button toggles power on/off
        board_button.on_press(cycle_animation)
        
        button.on_press(cycle_animation) 

        await uasyncio.gather(
            led_matrix.monitor(),
            button.monitor(),
            board_button.monitor(),
            auto_shutdown.monitor(),
        )
    except KeyboardInterrupt:
        print("Keyboard interrupt received")
        try:
            board_button.stop()
            auto_shutdown.stop()
            led_matrix.stop_animation()
            button.stop()
        except Exception as e:
            print("Error during cleanup:", str(e))
    except Exception as e:
        print("Error in main:", str(e))
        raise

if __name__ == "__main__":
    print("Initializing system...")
    uasyncio.run(main())
