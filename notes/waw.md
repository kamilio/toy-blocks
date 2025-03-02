## Play Simple WAV Files

For pre-recorded sounds in WAV format (8-bit, mono, 8-16kHz works best):

```python
from machine import Pin, I2S, SDCard
import os

# Mount SD card (simplify if using internal storage)
sd = SDCard(slot=2, miso=Pin(19), mosi=Pin(23), sck=Pin(18), cs=Pin(5))
os.mount(sd, '/sd')

# Simple WAV player for 8-bit WAV files
def play_wav(filename):
    # Set up I2S with simplified parameters
    audio_out = I2S(
        0,                  # I2S peripheral ID
        sck=Pin(26),        # Clock pin
        ws=Pin(25),         # Word select pin
        sd=Pin(22),         # Data pin
        mode=I2S.TX,        # Transmit mode
        bits=16,            # Audio bit depth
        format=I2S.MONO,    # Mono format
        rate=16000,         # Sample rate (Hz)
        ibuf=10000          # Buffer size
    )
    
    # Skip WAV header (44 bytes) and read audio data
    with open(filename, "rb") as file:
        header = file.read(44)  # Skip header
        
        # Read and play in chunks
        while True:
            audio_data = file.read(1024)
            if not audio_data:
                break
                
            # For 8-bit WAV, convert to 16-bit
            # (This is a simple conversion, not perfect)
            audio_samples = bytearray(len(audio_data) * 2)
            for i, sample in enumerate(audio_data):
                # Convert 8-bit (0-255) to 16-bit signed (-32768 to 32767)
                value = (sample - 128) * 256
                audio_samples[i*2] = value & 0xff
                audio_samples[i*2 + 1] = (value >> 8) & 0xff
                
            audio_out.write(audio_samples)
    
    # Clean up
    audio_out.deinit()

# Play a WAV file
play_wav("/sd/beep.wav")
```