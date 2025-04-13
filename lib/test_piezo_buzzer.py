import pytest
from lib.piezo_buzzer import PiezoBuzzer
from lib.piezo_buzzer_types import Note, Duration
from lib.piezo_buzzer_songs import COME_AS_YOU_ARE
import uasyncio

@pytest.mark.asyncio
async def test_piezo_buzzer_initialization():
    """Test that the piezo buzzer initializes correctly with default values"""
    buzzer = PiezoBuzzer(5)
    assert buzzer.pwm.freq == 440
    assert buzzer.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_piezo_buzzer_single_beep():
    """Test that the piezo buzzer can generate a single beep"""
    buzzer = PiezoBuzzer(5)
    await buzzer.beep()
    
    assert buzzer.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_piezo_buzzer_multiple_beeps():
    """Test that the piezo buzzer can generate multiple beeps"""
    buzzer = PiezoBuzzer(5)
    await buzzer.beep(count=2, duration_ms=200, interval_ms=150)
    
    assert buzzer.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_single_note_with_raw_values():
    """Test that the piezo buzzer can play a single note with Note and Duration objects"""
    buzzer = PiezoBuzzer(5)
    await buzzer.play_note(Note.F4, Duration.QUARTER)
    assert buzzer.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_single_note_with_integers():
    """Test that the piezo buzzer can play a single note with integer values"""
    buzzer = PiezoBuzzer(5)
    await buzzer.play_note(349, 250)  # F4, QUARTER
    assert buzzer.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_rest():
    """Test that the piezo buzzer can play a rest (silence)"""
    buzzer = PiezoBuzzer(5)
    await buzzer.play_note(Note.REST, Duration.QUARTER)
    assert buzzer.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_song():
    """Test that the piezo buzzer can play a complete song"""
    buzzer = PiezoBuzzer(5)
    await buzzer.play_song(COME_AS_YOU_ARE)
    assert buzzer.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_song_timing():
    """Test the timing pattern of notes played on the piezo buzzer"""
    buzzer = PiezoBuzzer(5)
    
    # Test song with two consecutive notes
    test_song = [
        (Note.C4, Duration.QUARTER),
        (Note.D4, Duration.QUARTER)
    ]
    
    # Track when notes are played
    note_sequence = []
    original_turn_on = buzzer._turn_on
    original_turn_off = buzzer._turn_off
    
    def track_on():
        note_sequence.append('on')
        original_turn_on()
    
    def track_off():
        note_sequence.append('off')
        original_turn_off()
    
    buzzer._turn_on = track_on
    buzzer._turn_off = track_off
    
    await buzzer.play_song(test_song)
    
    # Verify sequence of events (on-off-gap-on-off)
    assert note_sequence == ['on', 'off', 'on', 'off'], "Notes should follow on-off-on-off pattern"
