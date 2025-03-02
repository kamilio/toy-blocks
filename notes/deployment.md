# MicroPython Deployment Instructions

## Method 1: Using Pymakr in VSCode (Recommended)

1. Connect your microcontroller via USB
2. Open project in VSCode
3. Use Pymakr sidebar:
   - Click "Upload Project" to deploy all files
   - This will transfer main.py, boot.py, and all lib/ dependencies

## Method 2: Using mpremote

```bash
mpremote connect <PORT> cp -r . :
```

## Method 3: Using ampy

```bash
ampy --port <PORT> put main.py
ampy --port <PORT> put boot.py
ampy --port <PORT> put lib
```

## After Deployment

The device will execute:
1. boot.py first
2. main.py second, which:
   - Initializes auto shutdown (600s timeout)
   - Starts debug LED sequence
   - Enters main loop with sleep management

### Using Board Configurations

```python
from board_config import BoardConfig

# Initialize board configuration
board = BoardConfig('devkit1')  # or 'ttgo', or 'default'

# Use board-specific pins
led_pin = board.led_pin
i2c_scl = board.i2c_scl
```

Ensure all physical connections match pin configurations in code, particularly:
- Debug LED pins
- MPU6050 connections (if used)
- Any other sensors/actuators