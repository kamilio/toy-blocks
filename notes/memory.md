### 1. Use Internal Flash Storage

ESP32 already has built-in flash memory that MicroPython uses:

```python
# Simply use the built-in filesystem
import os

# List files in root directory
print(os.listdir())

# Write to a file
with open('myfile.txt', 'w') as f:
    f.write('Hello ESP32!')

# Read from a file
with open('myfile.txt', 'r') as f:
    content = f.read()
    print(content)
```

No additional hardware needed! However, this is limited to the available flash space after MicroPython is installed.

### 2. Use External SPI Flash (Simpler than SD Card)

A small SPI flash chip (like W25Q32) requires fewer components:

```python
from machine import SPI, Pin
import os
from spiflash import SPIFlash

# Initialize SPI
spi = SPI(1, baudrate=5000000, polarity=0, phase=0)
cs = Pin(5, Pin.OUT, value=1)

# Mount flash
flash = SPIFlash(spi, cs)
os.VfsFat.mkfs(flash)
os.mount(flash, '/flash')

# Now use it like regular storage
with open('/flash/data.txt', 'w') as f:
    f.write('Data saved to external flash')
```

This requires just 4 pins and is physically smaller than an SD card module.

### 3. USB Flash Drive

If your ESP32 board supports USB host mode (like ESP32-S2/S3):

```python
import os
import usb_storage

# Mount USB drive when inserted
usb = usb_storage.USB_Storage()
os.mount(usb, '/usb')

# Use like normal storage
print(os.listdir('/usb'))
```

### 4. I2C EEPROM

For smaller storage needs, I2C EEPROM chips are very simple to connect (just 2 data pins):

```python
from machine import I2C, Pin
import eepromi2c

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
eeprom = eepromi2c.EEPROM(i2c, 0x50)

# Write data
eeprom.write(0, b'Hello EEPROM!')

# Read data
data = eeprom.read(0, 13)
print(data.decode())
```