# main.py runs after boot.py and is meant for:
# - Your main application code
# - Program logic
# - Sleep/shutdown functions

import machine
from time import sleep, time
from auto_shutdown import AutoShutdown
from debug import Debug

auto_shutdown = AutoShutdown(timeout=600)
debug = Debug()

debug.blink(5)
debug.on()

while True:
    sleep(0.1)
    auto_shutdown.maybe_deepsleep()