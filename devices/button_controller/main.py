import uasyncio
from auto_shutdown import AutoShutdown
from button import DebouncedButton
from debug_led import DebugLed
from pin_config import PinConfigEsp32
from wifi import WiFi

class ButtonControllerPinConfig(PinConfigEsp32):
    """ESP32 pin configuration for button controller"""
    LED_PIN = 2
    BOOT_BUTTON = 0
    
    def is_builtin_led_active_low(self):
        return False

auto_shutdown = AutoShutdown(timeout=60)  # 60 seconds = 1 minute
wifi = WiFi()


async def handle_click():
    print('Button clicked!')
    await debug_led.blink(3, 0.2)


pin_config = ButtonControllerPinConfig()
debug_led = DebugLed(pin_config)
button = DebouncedButton(pin_config.BOOT_BUTTON)
button.on_press(handle_click)


async def main():
    try:
        await debug_led.blink(5)
        debug_led.on()

        await uasyncio.gather(
            button.monitor(),
            auto_shutdown.monitor(),
            wifi.connect_with_delay(delay=5),  # seconds
        )
    except KeyboardInterrupt:
        print('Keyboard interrupt received')
        button.stop()
    except Exception as e:
        print('Error in main:', str(e))
        raise


if __name__ == '__main__':
    print('Initializing system...')
    uasyncio.run(main())
