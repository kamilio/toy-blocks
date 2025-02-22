# main.py runs after boot.py and is meant for:
# - Your main application code
# - Program logic
# - Sleep/shutdown functions

import machine
from time import sleep, time
from and_gate import ANDGate
from auto_shutdown import AutoShutdown
from pins import GPIO14, GPIO15, GPIO13

and_gate = ANDGate(input1_pin=GPIO14, input2_pin=GPIO14, output_pin=GPIO13)
auto_shutdown = AutoShutdown(timeout=600)

while True:
    and_gate.compute()
    sleep(0.1)
    auto_shutdown.maybe_deepsleep()