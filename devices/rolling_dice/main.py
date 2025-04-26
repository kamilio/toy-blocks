import uasyncio
from auto_shutdown import AutoShutdown
from button import Button, DebouncedButton
from capacitive_touch_sensor import CapacitiveTouchSensor
from machine import Pin
from rolling_dice import RollingDice
from pin_config import PinConfigEsp32C3


class PinConfig(PinConfigEsp32C3):
    # Dice LED Pins
    # Layout reference:
    #    TL    TR
    #     MID
    #    BL    BR
    #    LL    LR
    rolling_dice_tl = 5  # Top Left
    rolling_dice_tr = 4  # Top Right
    rolling_dice_mid = 12  # Middle
    rolling_dice_bl = 6  # Bottom Left
    rolling_dice_br = 13  # Bottom Right
    rolling_dice_ll = 7  # Lower Left
    rolling_dice_lr = 2  # Lower Right
    
    # Button pins
    touch_button = 20
    reed_switch = 10

async def main():
    try:
        auto_shutdown = AutoShutdown(timeout=600)  # 600 seconds = 10 minutes
        rolling_dice = RollingDice([
            PinConfig.rolling_dice_tl,
            PinConfig.rolling_dice_tr,
            PinConfig.rolling_dice_mid,
            PinConfig.rolling_dice_bl,
            PinConfig.rolling_dice_br,
            PinConfig.rolling_dice_ll,
            PinConfig.rolling_dice_lr,
        ])

        reed_switch = Button(pin=PinConfig.reed_switch, pin_mode=Pin.IN, pull=Pin.PULL_UP)

        # Set up dice roll handler
        async def handle_roll():
            was_pressed = reed_switch.consume_was_pressed()
            await rolling_dice.roll(6 if was_pressed else None)

        # Set up BOOT button
        boot_button = DebouncedButton(PinConfig.BOOT_BUTTON)
        boot_button.on_press(handle_roll)

        # Set up capacitive touch sensor with our specialized class
        touch_sensor = CapacitiveTouchSensor(
            pin=PinConfig.touch_button,
            pull_down=True,  # Use pull-down resistor
            active_high=True,  # TTP223 outputs HIGH when touched
            debounce_ms=50,  # 50ms debounce to avoid false triggers
        )

        # Control LED with touch state and roll dice on touch
        async def on_touch():
            await handle_roll()  # Roll dice when touched

        # Register the callbacks
        touch_sensor.on_touch(on_touch)

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
