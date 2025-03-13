import sys
import os
import wave
import math
import struct
import asyncio
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.speaker_types import Note, Duration
from lib.songs import smoke_on_the_water

class LaptopSpeaker:
    def __init__(self):
        self.sample_rate = 44100
        self.temp_dir = tempfile.mkdtemp()
        self.tone_file = os.path.join(self.temp_dir, "tone.wav")
        
    def _generate_sine_wave(self, freq, duration_ms):
        num_samples = int((duration_ms / 1000.0) * self.sample_rate)
        audio_data = []
        for i in range(num_samples):
            sample = math.sin(2 * math.pi * int(freq) * i / self.sample_rate)
            audio_data.append(int(sample * 32767))
            
        with wave.open(self.tone_file, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(struct.pack('h' * len(audio_data), *audio_data))
    
    async def play_note(self, note, duration) -> None:
        if not isinstance(note, Note):
            note = Note.from_int(note)
        if not isinstance(duration, Duration):
            duration = Duration.from_int(duration)
        if note != Note.REST:
            self._generate_sine_wave(note, 100)  # Generate a short tone
            os.system(f"afplay {self.tone_file}")
        await asyncio.sleep(duration / 1000)
    
    async def play_song(self, song):
        for note, duration in song:
            await self.play_note(note, duration)
            if note != Note.REST:
                await asyncio.sleep(0.05)

async def main():
    speaker = LaptopSpeaker()
    await speaker.play_song(smoke_on_the_water)

if __name__ == "__main__":
    asyncio.run(main())