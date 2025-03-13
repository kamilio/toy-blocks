from led import Led

def test_led_initialization(mock_pin):
    pin = mock_pin(5)
    led = Led(5)
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