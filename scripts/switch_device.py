#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from typing import Optional


def merge_pymakr_config(device_type: str, project_root: Path, device_dir: Path):
    template_path = project_root / 'templates' / 'pymakr.conf.template'
    override_path = device_dir / 'pymakr_overrides.conf'

    with open(template_path) as f:
        template_config = json.load(f)

    if override_path.exists():
        with open(override_path) as f:
            override_config = json.load(f)
        template_config.update(override_config)

    template_config['name'] = device_type
    template_config['py_ignore'] = [i for i in template_config['py_ignore'] if i != 'devices/*']

    with open(project_root / 'pymakr.conf', 'w') as f:
        json.dump(template_config, f, indent=4)


def create_symlink(src: Path, dest: Path):
    if dest.exists() or dest.is_symlink():
        dest.unlink()
    os.symlink(str(src), str(dest))


def switch_device(device_type: str, project_root: Optional[Path] = None):
    if project_root is None:
        project_root = Path(__file__).parent.parent

    device_dir = project_root / 'devices' / device_type

    if not device_dir.exists():
        print(f"Error: Device type '{device_type}' does not exist")
        sys.exit(1)

    # Handle main.py symlink
    device_main = device_dir / 'main.py'
    if not device_main.exists():
        print(f'Error: {device_main} does not exist')
        sys.exit(1)
    create_symlink(device_main, project_root / 'main.py')

    # Handle boot.py symlink
    device_boot = device_dir / 'boot.py'
    template_boot = project_root / 'templates' / 'boot.py.template'
    if device_boot.exists():
        create_symlink(device_boot, project_root / 'boot.py')
    elif template_boot.exists():
        create_symlink(template_boot, project_root / 'boot.py')

    # Handle pymakr config
    merge_pymakr_config(device_type, project_root, device_dir)

    # Determine boot.py status message
    if device_boot.exists():
        boot_msg = 'Symlinked device-specific boot.py'
    elif template_boot.exists():
        boot_msg = 'Default boot.py'
    else:
        boot_msg = 'No boot.py found'

    print(f"""
Switched to device: {device_type}
  - Symlinked main.py
  - {boot_msg}
  - Created merged pymakr.conf
""")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: switch_device.py <device_type>')
        print('Example: switch_device.py button_controller')
        sys.exit(1)

    switch_device(sys.argv[1])
