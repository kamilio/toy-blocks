from led import Led


class MockVirtualPin:
    def __init__(self):
        self._value = 0

    def value(self, val=None):
        if val is not None:
            self._value = val
            return None
        return self._value


def test_led_with_virtual_pin():
    virtual_pin = MockVirtualPin()
    led = Led(virtual_pin)
    led.on()
    assert virtual_pin.value() == 1


def test_led_initialization(mock_pin):
    pin = mock_pin(5)
    Led(5)
    assert pin.mode == pin.OUT
    assert pin.value() == 0


def test_led_on(mock_pin):
    pin = mock_pin(5)
    led = Led(5)
    led.on()
    assert pin.value() == 1


def test_led_off(mock_pin):
    pin = mock_pin(5)
    led = Led(5)
    led.on()
    led.off()
    assert pin.value() == 0


def test_led_toggle(mock_pin):
    pin = mock_pin(5)
    led = Led(5)

    led.toggle()
    assert pin.value() == 1

    led.toggle()
    assert pin.value() == 0


def test_active_low_led(mock_pin):
    pin = mock_pin(5)
    led = Led(5, active_low=True)

    led.on()
    assert pin.value() == 0

    led.off()
    assert pin.value() == 1


def test_sequential_led_animation(mock_pin):
    # Create 7 LEDs using pins 1-7
    leds = []
    pins = []
    for i in range(7):
        pin = mock_pin(i + 1)
        pins.append(pin)
        leds.append(Led(i + 1))

    # Turn on LEDs one by one
    for i in range(7):
        leds[i].on()
        assert pins[i].value() == 1
        # Verify previous LEDs stay on
        for j in range(i):
            assert pins[j].value() == 1

    # Turn off LEDs one by one from last to first
    for i in range(6, -1, -1):
        leds[i].off()
        assert pins[i].value() == 0
        # Verify previous LEDs stay off
        for j in range(6, i, -1):
            assert pins[j].value() == 0
        # Verify remaining LEDs stay on
        for j in range(i):
            assert pins[j].value() == 1


def test_ping_pong_animation(mock_pin):
    # Create 7 LEDs using pins 1-7
    leds = []
    pins = []
    for i in range(7):
        pin = mock_pin(i + 1)
        pins.append(pin)
        leds.append(Led(i + 1))

    # Move LED from left to right
    for i in range(7):
        # Clear previous LED if not first
        if i > 0:
            leds[i - 1].off()
            assert pins[i - 1].value() == 0
        leds[i].on()
        assert pins[i].value() == 1

    # Move LED from right to left
    for i in range(5, -1, -1):
        # Clear previous LED
        leds[i + 1].off()
        assert pins[i + 1].value() == 0
        leds[i].on()
        assert pins[i].value() == 1
        # Verify all other LEDs are off
        for j in range(7):
            if j != i:
                assert pins[j].value() == 0


def test_binary_counter_animation(mock_pin):
    # Create 7 LEDs using pins 1-7
    leds = []
    pins = []
    for i in range(7):
        pin = mock_pin(i + 1)
        pins.append(pin)
        leds.append(Led(i + 1))

    # Count from 0 to 7 in binary
    for number in range(8):
        # Clear all LEDs first
        for led in leds:
            led.off()

        # Set binary representation
        binary = format(number, '07b')
        for i, bit in enumerate(binary):
            if bit == '1':
                leds[i].on()
                assert pins[i].value() == 1
            else:
                assert pins[i].value() == 0
