#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess
from typing import Dict, Any

BOARDS = {
    "esp32": {
        "name": "ESP32-WROOM",
        "chip": "esp32",
        "port": "/dev/tty.usbserial-0001",
        "baud": "460800",
        "flash_mode": "dio",
        "flash_addr": "0x1000",
        "firmware": "ESP32_GENERIC-20241129-v1.24.1.bin"
    },
    "esp32-c3": {
        "name": "ESP32-C3 SuperMini",
        "chip": "esp32c3",
        "port": "/dev/tty.usbmodem101",
        "baud": "460800",
        "flash_mode": "dio",
        "flash_addr": "0x0",
        "firmware": "ESP32_GENERIC_C3-20241129-v1.24.1.bin"
    }
}

def get_default_firmware(board_type: str) -> str:
    bin_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin")
    return os.path.join(bin_dir, BOARDS[board_type]["firmware"])

def flash_esp32(board_config: Dict[str, Any], port: str, firmware: str) -> bool:
    try:
        print(f"Flashing {board_config['name']}...")
        print(f"Erasing flash on {port}...")
        subprocess.run(["esptool.py", "--port", port, "erase_flash"], check=True)
        
        print(f"Flashing {firmware} to {port}...")
        subprocess.run([
            "esptool.py",
            "--chip", board_config["chip"],
            "--port", port,
            "--baud", board_config["baud"],
            "write_flash",
            "-z", board_config["flash_addr"],
            firmware
        ], check=True)
        
        print("Successfully flashed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during flashing: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: esptool.py not found. Install it with: pip install esptool", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Flash MicroPython firmware to ESP32 boards")
    parser.add_argument("--board", "-b", choices=list(BOARDS.keys()), default="esp32",
                      help="Board type to flash")
    parser.add_argument("--port", "-p",
                      help="Serial port (overrides board default)")
    parser.add_argument("--firmware", "-f",
                      help="Firmware binary path (if not specified, uses board-specific default)")
    
    args = parser.parse_args()
    
    board_config = BOARDS[args.board]
    firmware = args.firmware or get_default_firmware(args.board)
    
    if not os.path.exists(firmware):
        print(f"Error: Firmware file not found: {firmware}", file=sys.stderr)
        print(f"Download the appropriate firmware for your board:", file=sys.stderr)
        print(f"ESP32: https://micropython.org/download/esp32/", file=sys.stderr)
        print(f"ESP32-C3: https://micropython.org/download/esp32c3/", file=sys.stderr)
        return 1
    
    port = args.port or board_config["port"]
    
    success = flash_esp32(board_config, port, firmware)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())