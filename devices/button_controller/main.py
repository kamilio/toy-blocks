import uasyncio
from auto_shutdown import AutoShutdown
from board_config import BoardConfig
from button import DebouncedButton
from debug_led import DebugLed
from wifi import WiFi

auto_shutdown = AutoShutdown(timeout=60)  # 600 seconds = 10 minutes
wifi = WiFi()


async def handle_click():
    print('Button clicked!')
    await debug_led.blink(3, 0.2)


board_config = BoardConfig()
debug_led = DebugLed(board_config=board_config)
button = DebouncedButton(board_config.BOOT_BUTTON)
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
