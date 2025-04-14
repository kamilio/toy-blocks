import uasyncio
from auto_shutdown import AutoShutdown
from board_config import BoardConfig
from button import Button, DebouncedButton
from capacitive_touch_sensor import CapacitiveTouchSensor
from debug_led import DebugLed
from machine import Pin
from rolling_dice import RollingDice


async def main():
    try:
        board_config = BoardConfig(detected_board='ESP32-C3')
        auto_shutdown = AutoShutdown(timeout=600)  # 600 seconds = 10 minutes
        rolling_dice = RollingDice(board_config.dice_pins)
        debug_led = DebugLed(board_config)

        reed_switch = Button(pin=10, pin_mode=Pin.IN, pull=Pin.PULL_UP)

        # Turn off the LED initially
        debug_led.off()

        # Set up dice roll handler
        async def handle_roll():
            was_pressed = reed_switch.consume_was_pressed()
            await rolling_dice.roll(6 if was_pressed else None)

        # Set up BOOT button
        boot_button = DebouncedButton(board_config.BOOT_BUTTON)
        boot_button.on_press(handle_roll)

        # Set up capacitive touch sensor with our specialized class
        touch_sensor = CapacitiveTouchSensor(
            pin=board_config.TTP223_BUTTON,
            pull_down=True,  # Use pull-down resistor
            active_high=True,  # TTP223 outputs HIGH when touched
            debounce_ms=50,  # 50ms debounce to avoid false triggers
        )

        # Control LED with touch state and roll dice on touch
        async def on_touch():
            debug_led.on()  # Turn LED ON when touched
            await handle_roll()  # Roll dice when touched

        async def on_release():
            debug_led.off()  # Turn LED OFF when not touched

        # Register the callbacks
        touch_sensor.on_touch(on_touch)
        touch_sensor.on_release(on_release)

        # Initial roll on startup
        await rolling_dice.roll()

        print('Dice system running...')
        await uasyncio.gather(
            boot_button.monitor(),
            touch_sensor.monitor(),
            auto_shutdown.monitor(),
            reed_switch.monitor(),
            return_exceptions=True,
        )
    except KeyboardInterrupt:
        print('Keyboard interrupt received')
        try:
            boot_button.stop()
            touch_sensor.stop()
            auto_shutdown.stop()
            reed_switch.stop()
            rolling_dice.clear()
        except Exception as e:
            print('Error during cleanup:', str(e))
    except Exception as e:
        print('Error in main:', str(e))
        raise


if __name__ == '__main__':
    uasyncio.run(main())
