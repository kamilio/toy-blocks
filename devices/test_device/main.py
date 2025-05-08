import uasyncio as asyncio
from lib.pin_config import PinConfigEsp32C3
from lib.verify_sd_card_reader import verify_sd_card_reader
from lib.debug_led import DebugLed


class TestDevicePinConfig(PinConfigEsp32C3):
    """ESP32-C3 pin configuration for test device"""
    # SPI pins for SD card reader
    SPI_MOSI = 7
    SPI_MISO = 6
    SPI_CLK = 8
    SPI_CS = 10


async def main():
    # Initialize pin configuration
    pin_config = TestDevicePinConfig()
    
    # Initialize debug LED
    debug_led = DebugLed(pin_config)
    await debug_led.blink(count=1, interval=0.5)  # Indicate startup
    
    try:
        # Test SD card reader functionality
        await verify_sd_card_reader(pin_config)
        
        # Indicate successful verification
        await debug_led.blink(count=3, interval=0.2)
        
    except Exception as e:
        print(f"SD card verification failed: {e}")
        # Indicate failure
        await debug_led.blink(count=5, interval=0.1)
        
    finally:
        debug_led.off()


if __name__ == "__main__":
    asyncio.run(main())
