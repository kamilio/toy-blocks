# Flashing MicroPython to ESP32 - Quick Command Guide

## Prerequisites

```bash
# Install esptool.py if not already installed
pip install esptool
```

## Download MicroPython

Download the latest ESP32 firmware from the [MicroPython downloads page](`https://micropython.org/download/esp32/`).

## Connect the ESP32

1. Connect your ESP32 to your computer via USB

```bash
ls /dev/tty.* 
# Look for something like /dev/tty.usbserial-0001
```

## Flash

```
./script/flash_esp32.py
```