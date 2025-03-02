import sys
import os
import wave
import math
import struct
from time import sleep
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.speaker_types import Note, Duration
from lib.songs import COME_AS_YOU_ARE

class LaptopSpeaker:
    def __init__(self):
        self.sample_rate = 44100
        self.temp_dir = tempfile.mkdtemp()
        self.tone_file = os.path.join(self.temp_dir, "tone.wav")
        
    def _generate_sine_wave(self, freq, duration_ms):
        num_samples = int((duration_ms / 1000.0) * self.sample_rate)
        audio_data = []
        for i in range(num_samples):
            sample = math.sin(2 * math.pi * freq * i / self.sample_rate)
            audio_data.append(int(sample * 32767))
            
        with wave.open(self.tone_file, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(struct.pack('h' * len(audio_data), *audio_data))
    
    def play_note(self, note: Note, duration: Duration) -> None:
        if note != Note.REST:
            self._generate_sine_wave(note, 100)  # Generate a short tone
            os.system(f'afplay {self.tone_file}')
        sleep(duration / 1000)
    
    def play_song(self, song: list[tuple[Note, Duration]]) -> None:
        for note, duration in song:
            self.play_note(note, duration)
            if note != Note.REST:
                sleep(0.05)  # Small gap between notes

def main():
    speaker = LaptopSpeaker()
    print("Playing 'Come As You Are' by Nirvana...")
    speaker.play_song(COME_AS_YOU_ARE)

if __name__ == "__main__":
    main()