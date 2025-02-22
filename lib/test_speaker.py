from lib.speaker import Speaker, Note, Duration
from lib.songs import COME_AS_YOU_ARE

def test_speaker_initialization():
    speaker = Speaker(5, 6)
    assert speaker.pwm1.freq == 440
    assert speaker.pwm2.freq == 440
    assert speaker.pwm1.duty_u16 == 0
    assert speaker.pwm2.duty_u16 == 0

def test_speaker_single_beep():
    speaker = Speaker(5, 6)
    speaker.beep()
    
    # Should turn on then off the PWMs
    assert speaker.pwm1.duty_u16 == 0
    assert speaker.pwm2.duty_u16 == 0

def test_speaker_multiple_beeps():
    speaker = Speaker(5, 6)
    speaker.beep(count=2, duration_ms=200, interval_ms=150)
    
    # Final state should be off
    assert speaker.pwm1.duty_u16 == 0
    assert speaker.pwm2.duty_u16 == 0

def test_play_single_note():
    speaker = Speaker(5, 6)
    speaker.play_note(Note.F4, Duration.QUARTER)
    
    # After playing, PWMs should be off
    assert speaker.pwm1.duty_u16 == 0
    assert speaker.pwm2.duty_u16 == 0

def test_play_song():
    speaker = Speaker(5, 6)
    speaker.play_song(COME_AS_YOU_ARE)
    assert speaker.pwm1.duty_u16 == 0
    assert speaker.pwm2.duty_u16 == 0