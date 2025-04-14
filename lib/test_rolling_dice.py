import pytest
from uasyncio_mock import mock_sleep, reset_mock_sleep

from lib.rolling_dice import RollingDice
from lib.shift_register import ShiftRegister


@pytest.fixture(autouse=True)
def reset_sleep():
    reset_mock_sleep()


@pytest.mark.asyncio
async def test_dice_roll(mocker):
    """Test the async roll function"""
    shift_register = ShiftRegister(5, 6, 7)
    virtual_pins = [(shift_register, i) for i in range(7)]
    dice = RollingDice(virtual_pins)

    # Mock random to get consistent results
    mocker.patch('random.randint', return_value=6)

    # Execute roll
    result = await dice.roll()

    # Verify final number
    assert result == 6
    assert dice.current_number == 6

    # Verify proper animation execution
    assert mock_sleep.call_count > 0, 'Animation should have sleep calls'
    assert result == 6, 'Should return the mocked value'
    assert dice.animation_count == dice.ANIMATION_STEPS, 'Should complete all animation steps'

    # Verify final LED pattern matches the result
    pattern = dice.DICE_PATTERNS[result]
    for led, expected_value in zip(dice.leds, pattern):
        assert led.led.value() == expected_value


@pytest.mark.asyncio
async def test_rolling_dice_gpio_initialization():
    pins = [5, 6, 7, 8, 9, 10, 11]
    dice = RollingDice(pins)
    assert len(dice.leds) == 7
    assert dice.current_number is None


@pytest.mark.asyncio
async def test_rolling_dice_shift_register_initialization():
    shift_register = ShiftRegister(5, 6, 7)
    virtual_pins = [(shift_register, i) for i in range(7)]
    dice = RollingDice(virtual_pins)
    assert len(dice.leds) == 7
    assert dice.current_number is None
    # All LEDs should be off initially
    for led in dice.leds:
        assert led.led.value() == 0


@pytest.mark.asyncio
async def test_dice_display_pattern():
    pins = [5, 6, 7, 8, 9, 10, 11]
    dice = RollingDice(pins)

    # Test pattern for number 1 (center only)
    dice.display_number(1)
    assert dice.current_number == 1
    for i, led in enumerate(dice.leds):
        if i == 2:  # Center LED
            assert led.led.value() == 1
        else:
            assert led.led.value() == 0


@pytest.mark.asyncio
async def test_dice_shift_register_display_pattern():
    shift_register = ShiftRegister(5, 6, 7)
    virtual_pins = [(shift_register, i) for i in range(7)]
    dice = RollingDice(virtual_pins)

    # Test pattern for number 1 (center only)
    dice.display_number(1)
    assert dice.current_number == 1
    for i, led in enumerate(dice.leds):
        if i == 2:  # Center LED
            assert led.led.value() == 1
        else:
            assert led.led.value() == 0


@pytest.mark.asyncio
async def test_dice_clear():
    shift_register = ShiftRegister(5, 6, 7)
    virtual_pins = [(shift_register, i) for i in range(7)]
    dice = RollingDice(virtual_pins)

    # First set all LEDs on
    for led in dice.leds:
        led.on()
    # Verify all LEDs are on
    for led in dice.leds:
        assert led.led.value() == 1

    # Then clear them
    dice.clear()
    # Verify all LEDs are off
    for led in dice.leds:
        assert led.led.value() == 0


@pytest.mark.asyncio
async def test_dice_cycle_number():
    shift_register = ShiftRegister(5, 6, 7)
    virtual_pins = [(shift_register, i) for i in range(7)]
    dice = RollingDice(virtual_pins)

    # First cycle should show test pattern (all LEDs)
    dice.cycle_number()
    assert all(led.led.value() == 1 for led in dice.leds)

    # Second cycle should show number 1
    dice.cycle_number()
    assert dice.current_number == 1
    for i, led in enumerate(dice.leds):
        if i == 2:  # Center LED
            assert led.led.value() == 1
        else:
            assert led.led.value() == 0


@pytest.mark.asyncio
async def test_dice_debug_display_gpio(capsys):
    pins = [5, 6, 7, 8, 9, 10, 11]
    dice = RollingDice(pins)
    capsys.readouterr()  # Clear previous output

    dice.debug_display()
    captured = capsys.readouterr()

    expected_output = """
Dice LED Pin Layout:

   5     6
   (TL)   (TR)

      7
    (MID)

   8     9
   (BL)   (BR)

   10     11
   (LL)   (LR)"""

    assert captured.out.strip() == expected_output.strip()


@pytest.mark.asyncio
async def test_dice_debug_display_shift_register(capsys):
    shift_register = ShiftRegister(5, 6, 7)
    virtual_pins = [(shift_register, i) for i in range(7)]
    dice = RollingDice(virtual_pins)
    capsys.readouterr()  # Clear previous output

    dice.debug_display()
    captured = capsys.readouterr()

    expected_output = """
Dice LED Pin Layout:

   (sr_0,0)     (sr_0,1)
   (TL)   (TR)

      (sr_0,2)
    (MID)

   (sr_0,3)     (sr_0,4)
   (BL)   (BR)

   (sr_0,5)     (sr_0,6)
   (LL)   (LR)"""

    assert captured.out.strip() == expected_output.strip()
