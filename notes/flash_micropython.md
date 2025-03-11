# Flashing MicroPython to ESP32 - Quick Command Guide

## Prerequisites

```bash
# Install esptool.py if not already installed
pip install esptool
```

## Download MicroPython Firmware

Each board type requires its specific firmware:

### ESP32-WROOM
Download from [MicroPython ESP32 downloads](https://micropython.org/download/esp32/)
- Save as `bin/ESP32_GENERIC-20241129-v1.24.1.bin`

### ESP32-C3 SuperMini
Download from [MicroPython ESP32-C3 downloads](https://micropython.org/download/esp32c3/)
- Save as `bin/ESP32_C3_GENERIC-20240105-v1.22.1.bin`

## Connect the ESP32

1. Connect your ESP32 to your computer via USB

```bash
ls /dev/tty.* 
# Look for:
# ESP32-WROOM: /dev/tty.usbserial-0001
# ESP32-C3 SuperMini: /dev/tty.usbmodem1101
```

## Flash

For ESP32-WROOM (default):
```bash
./scripts/flash_esp32_micropython.py --board esp32
```

For ESP32-C3 SuperMini:
```bash
./scripts/flash_esp32_micropython.py --board esp32-c3
```

You can override the default port if needed:
```bash
./scripts/flash_esp32_micropython.py --board esp32 --port /dev/tty.usbserial-XXXX
```

Custom firmware path:
```bash
./scripts/flash_esp32_micropython.py --board esp32 --firmware path/to/firmware.bin
```

## Directory Structure

```
toy-blocks/
├── bin/
│   ├── ESP32_GENERIC-20241129-v1.24.1.bin     # For ESP32-WROOM
│   └── ESP32_C3_GENERIC-20240105-v1.22.1.bin  # For ESP32-C3
└── scripts/
    └── flash_esp32_micropython.py