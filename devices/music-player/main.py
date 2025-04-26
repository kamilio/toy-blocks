import uasyncio

from lib.audio_amplifier import AudioAmplifier
from lib.auto_shutdown import AutoShutdown
from lib.debug_led import DebugLed
from lib.pin_config import PinConfigEsp32
from lib.sd_card_reader import SDCardReader

# Hardcoded WAV file path on SD card
WAV_FILE_PATH = '/song.wav'


class MusicPlayerPinConfig(PinConfigEsp32):
    """ESP32 pin configuration for music player"""
    SPI_MOSI = 23
    SPI_MISO = 19
    SPI_CLK = 18
    SPI_CS = 5
    LED_PIN = 2
    sound_pin = 4
    
    def is_builtin_led_active_low(self):
        return False


async def main():
    try:
        # Initialize pin configuration
        pin_config = MusicPlayerPinConfig()

        # Set up auto shutdown after 10 minutes of inactivity
        auto_shutdown = AutoShutdown(timeout=600)  # 600 seconds = 10 minutes

        # Initialize debug LED
        debug_led = DebugLed(pin_config)

        # Initialize SD card reader
        sd_reader = SDCardReader(
            sck_pin=pin_config.SPI_CLK,
            mosi_pin=pin_config.SPI_MOSI,
            miso_pin=pin_config.SPI_MISO,
            cs_pin=pin_config.SPI_CS,
        )

        # Initialize the SD card
        await sd_reader.initialize()

        # Initialize audio amplifier (using PAM8403 analog amplifier)
        # You can change to MAX98357A if you're using that amplifier
        amplifier = AudioAmplifier(
            data_pin=pin_config.sound_pin,
            amp_type=AudioAmplifier.PAM8403,
            volume=80,  # Set initial volume to 80%
        )

        print(f'Playing WAV file: {WAV_FILE_PATH}')

        # Optionally add other event handlers
        async def on_playback_started(status):
            print('Playback started')

        async def on_playback_completed(status):
            print('Playback completed')

        amplifier.on_playback_started(on_playback_started)
        amplifier.on_playback_completed(on_playback_completed)

        # Start monitoring amplifier status
        await amplifier.monitor()

        # Play the WAV file
        success = await amplifier.play_wav(sd_reader, WAV_FILE_PATH)
        if not success:
            print(f'Failed to play {WAV_FILE_PATH}')
            await debug_led.blink(count=3, interval=0.2)  # Error indicator

        print('Music player running...')
        await uasyncio.gather(auto_shutdown.monitor(), sd_reader.monitor(), return_exceptions=True)

    except KeyboardInterrupt:
        print('Keyboard interrupt received')
        await cleanup(amplifier, debug_led, sd_reader)
    except Exception as e:
        print('Error in main:', str(e))
        await cleanup(amplifier, debug_led, sd_reader)
        raise


async def cleanup(amplifier=None, debug_led=None, sd_reader=None):
    """Clean up resources"""
    try:
        if amplifier:
            await amplifier.stop()
        if debug_led:
            debug_led.off()
        if sd_reader:
            sd_reader.stop()
    except Exception as e:
        print('Error during cleanup:', str(e))


if __name__ == '__main__':
    uasyncio.run(main())
