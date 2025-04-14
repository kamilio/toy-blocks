import machine


class ANDGate:
    def __init__(self, input1_pin, input2_pin, output_pin):
        self.input1 = machine.Pin(input1_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.input2 = machine.Pin(input2_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.output = machine.Pin(output_pin, machine.Pin.OUT)

    def compute(self):
        result = self.input1.value() and self.input2.value()
        self.output.value(result)
        return result
