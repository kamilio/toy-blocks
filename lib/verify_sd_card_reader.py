import uasyncio as asyncio
from sd_card_reader import SDCardReader

async def verify_sd_card_reader(pin_config):
    # Get SD card pins from the pin configuration
    sck_pin = pin_config.SPI_CLK
    mosi_pin = pin_config.SPI_MOSI
    miso_pin = pin_config.SPI_MISO
    cs_pin = pin_config.SPI_CS
    
    # Initialize SD card reader
    sd = SDCardReader(sck_pin, mosi_pin, miso_pin, cs_pin)
    
    # Initialize the SD card
    print("Initializing SD card...")
    await sd.initialize()
    print("SD card initialized")
    
    # Read the esp32.txt file
    print("Reading esp32.txt...")
    data = await sd.read_file("esp32.txt")
    
    # Print content
    print("\nFile content:")
    if isinstance(data, bytes):
        print(data.decode('utf-8'))
    else:
        print(data)
    
    # Clean shutdown
    sd.stop()