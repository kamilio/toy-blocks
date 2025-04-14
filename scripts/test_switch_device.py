import json

import pytest
from switch_device import create_symlink, merge_pymakr_config, switch_device


@pytest.fixture
def mock_project(tmp_path):
    project_dir = tmp_path / 'project'
    project_dir.mkdir()

    # Create device directories
    devices_dir = project_dir / 'devices' / 'test_device'
    devices_dir.mkdir(parents=True)

    # Create templates directory
    templates_dir = project_dir / 'templates'
    templates_dir.mkdir()

    # Create template config
    template_config = {'name': 'ESP32 Project', 'py_ignore': ['devices/*', 'test_*.py']}
    with open(templates_dir / 'pymakr.conf.template', 'w') as f:
        json.dump(template_config, f)

    # Create device files
    with open(devices_dir / 'main.py', 'w') as f:
        f.write("print('test device')")

    with open(devices_dir / 'pymakr_overrides.conf', 'w') as f:
        json.dump({'address': '/dev/test'}, f)

    return project_dir


def test_merge_pymakr_config(mock_project):
    device_dir = mock_project / 'devices' / 'test_device'
    merge_pymakr_config('test_device', mock_project, device_dir)

    with open(mock_project / 'pymakr.conf') as f:
        merged = json.load(f)

    assert merged['name'] == 'test_device'
    assert merged['address'] == '/dev/test'
    assert 'devices/*' not in merged['py_ignore']


def test_create_symlink(tmp_path):
    src = tmp_path / 'source'
    dest = tmp_path / 'dest'

    with open(src, 'w') as f:
        f.write('test')

    create_symlink(src, dest)
    assert dest.is_symlink()
    assert dest.resolve() == src


def test_switch_device_success(mock_project):
    switch_device('test_device', project_root=mock_project)

    main_link = mock_project / 'main.py'
    assert main_link.is_symlink()
    assert main_link.resolve() == mock_project / 'devices' / 'test_device' / 'main.py'

    with open(mock_project / 'pymakr.conf') as f:
        config = json.load(f)
    assert config['name'] == 'test_device'


def test_switch_device_nonexistent(mock_project):
    with pytest.raises(SystemExit):
        switch_device('nonexistent_device', project_root=mock_project)
