import machine as Machine

class ANDGate:
    def __init__(self, input1_pin, input2_pin, output_pin):
        self.input1 = Machine.Pin(input1_pin, Machine.Pin.IN, Machine.Pin.PULL_UP)
        self.input2 = Machine.Pin(input2_pin, Machine.Pin.IN, Machine.Pin.PULL_UP)
        self.output = Machine.Pin(output_pin, Machine.Pin.OUT)
    
    def compute(self):
        result = self.input1.value() and self.input2.value()
        self.output.value(result)
        return result