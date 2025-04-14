import asyncio
import math
import os
import struct
import sys
import tempfile
import wave

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.piezo_buzzer_songs import SMOKE_ON_THE_WATER
from lib.piezo_buzzer_types import Duration, Note


class LaptopPiezoBuzzer:
    """
    A simulator for piezo buzzer that plays sounds through the laptop speakers
    This allows testing piezo buzzer songs on a development machine
    """

    def __init__(self):
        self.sample_rate = 44100
        self.temp_dir = tempfile.mkdtemp()
        self.tone_file = os.path.join(self.temp_dir, 'tone.wav')

    def _generate_sine_wave(self, freq, duration_ms):
        """Generate a sine wave with the given frequency and duration"""
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
        """Play a single note on the simulated piezo buzzer"""
        if not isinstance(note, Note):
            note = Note.from_int(note)
        if not isinstance(duration, Duration):
            duration = Duration.from_int(duration)
        if note != Note.REST:
            self._generate_sine_wave(note, 100)  # Generate a short tone
            os.system(f'afplay {self.tone_file}')
        await asyncio.sleep(duration / 1000)

    async def play_song(self, song):
        """Play a sequence of notes (song) on the simulated piezo buzzer"""
        for note, duration in song:
            await self.play_note(note, duration)
            if note != Note.REST:
                await asyncio.sleep(0.05)


async def main():
    """
    Main function to demonstrate piezo buzzer capabilities
    by playing a song using the laptop audio as a simulation
    """
    print('Playing song on simulated piezo buzzer...')
    buzzer = LaptopPiezoBuzzer()
    await buzzer.play_song(SMOKE_ON_THE_WATER)
    print('Piezo buzzer demonstration completed')


if __name__ == '__main__':
    asyncio.run(main())
