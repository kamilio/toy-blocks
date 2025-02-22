from time import sleep
from and_gate import ANDGate
from pins import GPIO14, GPIO15, GPIO13

and_gate = ANDGate(input1_pin=GPIO14, input2_pin=GPIO14, output_pin=GPIO13)

# Main loop
while True:
    and_gate.compute()
    sleep(0.1)