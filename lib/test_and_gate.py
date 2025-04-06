from and_gate import ANDGate

def test_and_gate():
    and_gate = ANDGate(1, 2, 3)
    assert and_gate.compute() == 0
    and_gate.input1.value(1)
    assert and_gate.compute() == 0
    and_gate.input2.value(1)
    assert and_gate.compute() == 1
    and_gate.input1.value(0)
    assert and_gate.compute() == 0
    and_gate.input2.value(0)
    assert and_gate.compute() == 0

