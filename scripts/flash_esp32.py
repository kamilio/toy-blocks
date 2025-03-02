#!/usr/bin/env python3

import argparse
import os
import sys
import subprocess

DEFAULT_PORT = "/dev/tty.usbserial-0001"  # Common port on Linux
DEFAULT_FIRMWARE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "bin", "ESP32_GENERIC-20241129-v1.24.1.bin")

def flash_esp32(port, firmware):
    try:
        # Erase flash
        print(f"Erasing flash on {port}...")
        subprocess.run(["esptool.py", "--port", port, "erase_flash"], check=True)
        
        # Flash firmware
        print(f"Flashing {firmware} to {port}...")
        subprocess.run([
            "esptool.py",
            "--chip", "esp32",
            "--port", port,
            "--baud", "460800",
            "write_flash",
            "-z", "0x1000",
            firmware
        ], check=True)
        
        print("Successfully flashed ESP32!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during flashing: {e}", file=sys.stderr)
        return False
    except FileNotFoundError:
        print("Error: esptool.py not found. Install it with: pip install esptool", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Flash MicroPython firmware to ESP32")
    parser.add_argument("--port", "-p", default=DEFAULT_PORT,
                      help=f"Serial port (default: {DEFAULT_PORT})")
    parser.add_argument("--firmware", "-f", default=DEFAULT_FIRMWARE,
                      help=f"Firmware binary path (default: {DEFAULT_FIRMWARE})")
    
    args = parser.parse_args()
    
    # Check if firmware exists
    if not os.path.exists(args.firmware):
        print(f"Error: Firmware file not found: {args.firmware}", file=sys.stderr)
        return 1
    
    success = flash_esp32(args.port, args.firmware)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())