import pytest
from lib.speaker import Speaker
from lib.speaker_types import Note, Duration
from lib.songs import COME_AS_YOU_ARE
import uasyncio

@pytest.mark.asyncio
async def test_speaker_initialization():
    speaker = Speaker(5)
    assert speaker.pwm.freq == 440
    assert speaker.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_speaker_single_beep():
    speaker = Speaker(5)
    await speaker.beep()
    
    assert speaker.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_speaker_multiple_beeps():
    speaker = Speaker(5)
    await speaker.beep(count=2, duration_ms=200, interval_ms=150)
    
    assert speaker.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_single_note_with_raw_values():
    speaker = Speaker(5)
    await speaker.play_note(Note.F4, Duration.QUARTER)
    assert speaker.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_single_note_with_integers():
    speaker = Speaker(5)
    await speaker.play_note(349, 250)  # F4, QUARTER
    assert speaker.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_rest():
    speaker = Speaker(5)
    await speaker.play_note(Note.REST, Duration.QUARTER)
    assert speaker.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_song():
    speaker = Speaker(5)
    await speaker.play_song(COME_AS_YOU_ARE)
    assert speaker.pwm.duty_u16 == 0

@pytest.mark.asyncio
async def test_play_song_timing():
    speaker = Speaker(5)
    
    # Test song with two consecutive notes
    test_song = [
        (Note.C4, Duration.QUARTER),
        (Note.D4, Duration.QUARTER)
    ]
    
    # Track when notes are played
    note_sequence = []
    original_turn_on = speaker._turn_on
    original_turn_off = speaker._turn_off
    
    def track_on():
        note_sequence.append('on')
        original_turn_on()
    
    def track_off():
        note_sequence.append('off')
        original_turn_off()
    
    speaker._turn_on = track_on
    speaker._turn_off = track_off
    
    await speaker.play_song(test_song)
    
    # Verify sequence of events (on-off-gap-on-off)
    assert note_sequence == ['on', 'off', 'on', 'off'], "Notes should follow on-off-on-off pattern"