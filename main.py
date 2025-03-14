import uasyncio
from auto_shutdown import AutoShutdown
from board_button import BoardButton
from debug_led import DebugLed

auto_shutdown = AutoShutdown(timeout=600)
debug = DebugLed()

async def handle_click():
    print("Button clicked!")
    await debug.blink(3, 0.2)

button = BoardButton(handle_click)

async def main():
    try:
        await debug.blink(5)
        debug.on()
        
        await uasyncio.gather(
            button.monitor_buttons(),
        )
    except KeyboardInterrupt:
        print("Keyboard interrupt received")
        button.stop()
    except Exception as e:
        print("Error in main:", str(e))
        raise

if __name__ == "__main__":
    print("Initializing system...")
    uasyncio.run(main())