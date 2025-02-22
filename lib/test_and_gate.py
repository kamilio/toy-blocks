from and_gate import ANDGate
from pins import GPIO25, GPIO26, GPIO27

AND_INPUT_A = GPIO25 
AND_INPUT_B = GPIO26 
AND_OUTPUT = GPIO27  

def test_and_gate():
    and_gate = ANDGate(AND_INPUT_A, AND_INPUT_B, AND_OUTPUT)
    assert and_gate.compute() == 0
    and_gate.input1.value(1)
    assert and_gate.compute() == 0
    and_gate.input2.value(1)
    assert and_gate.compute() == 1
    and_gate.input1.value(0)
    assert and_gate.compute() == 0
    and_gate.input2.value(0)
    assert and_gate.compute() == 0

