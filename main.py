# main.py runs after boot.py and is meant for:
# - Your main application code
# - Program logic
# - Sleep/shutdown functions

import machine
import uasyncio
from auto_shutdown import AutoShutdown
from debug_led import DebugLed

auto_shutdown = AutoShutdown(timeout=600)
debug = DebugLed()

async def main():
    await debug.blink(5)
    debug.on()
    
    while True:
        await uasyncio.sleep(0.1)
        auto_shutdown.maybe_deepsleep()

uasyncio.run(main())