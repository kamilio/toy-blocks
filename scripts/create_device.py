#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path

def create_device(device_type):
    project_root = Path(__file__).parent.parent
    device_dir = project_root / "devices" / device_type

    if device_dir.exists():
        print(f"Error: Device type '{device_type}' already exists")
        sys.exit(1)

    # Create device directory
    device_dir.mkdir(parents=True)

    # Create empty main.py
    with open(device_dir / "main.py", "w") as f:
        f.write("# Device-specific code for " + device_type + "\n")

    # Create device-specific pymakr overrides
    pymakr_conf = {
        "name": device_type,
        "address": "/dev/ttyUSB0",
        "upload_chunks": 128,
        "sync_file_types": ["py"],
        "sync_all_file_types": False,
        "sync_folder": "../../",
        "open_on_start": True,
        "safe_boot_on_upload": False,
        "py_ignore": [
            "**/*",
            "!lib/*.py",
            f"!devices/{device_type}/main.py",
            "**/test_*.py"
        ],
        "fast_upload": False
    }
    
    with open(device_dir / "pymakr_overrides.conf", "w") as f:
        json.dump(pymakr_conf, f, indent=4)

    print(f"""
Created new device type: {device_type}
  - Directory: {device_dir}
  - Created main.py
  - Created pymakr_overrides.conf

To use with VSCode Pymakr:
1. Open the device directory in VSCode:
   cd {device_dir}
   code .

2. Use Pymakr's Upload button to deploy the code

Next steps:
1. Implement your device code in {device_dir}/main.py
""")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: create_device.py <device_type>")
        print("Example: create_device.py temperature_monitor")
        sys.exit(1)

    create_device(sys.argv[1])