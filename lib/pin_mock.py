import pytest


class MockPin:
    IN = 'in'
    OUT = 'out'
    PULL_UP = 'pull_up'
    PULL_DOWN = 'pull_down'

    _instances = {}

    def __new__(cls, id, mode=OUT, pull=None):
        existing_instance = cls._instances.get(id)
        if existing_instance is not None:
            return existing_instance
        return super().__new__(cls)

    def __init__(self, id, mode=OUT, pull=None):
        if id not in self._instances:
            self.id = id
            self.mode = mode
            self._value = 0
            self.led = self  # Make pin act as its own LED for test compatibility
            self.history = []
            print(f'Created MockPin {id} with mode {mode}')
            self._instances[id] = self

    def value(self, val=None):
        if val is not None:
            val = int(bool(val))  # Convert to 0 or 1
            prev_value = self._value
            self._value = val
            if val != prev_value:  # Only add to history if value actually changed
                print(f'Pin {self.id} value changed from {prev_value} to {val}')
                self.history.append(val)
                print(f'History updated: {self.history}')
            else:
                print(f'Pin {self.id} value unchanged at {val}')
        return self._value

    def on(self):
        self.value(1)

    def off(self):
        self.value(0)

    def toggle(self):
        self.value(not self.value())

    @classmethod
    def clear_instances(cls):
        print('Clearing all pin instances')
        cls._instances.clear()


@pytest.fixture(scope='function', autouse=True)
def mock_pin():
    MockPin.clear_instances()
    return MockPin
