import pytest
from unittest.mock import MagicMock
import bluetooth
from lib.ble_beacon import BleBeacon, BLEError

@pytest.fixture
def mock_ble(monkeypatch):
    mock_bluetooth = MagicMock()
    mock_ble_instance = MagicMock()
    mock_bluetooth.BLE.return_value = mock_ble_instance
    monkeypatch.setattr(bluetooth, 'BLE', mock_bluetooth.BLE)
    return mock_ble_instance

def test_ble_beacon_initialization(mock_ble):
    """Test BLE beacon initialization with default name"""
    beacon = BleBeacon()
    
    assert beacon.name == "MyBeacon"
    mock_ble.active.assert_called_once_with(True)

def test_ble_beacon_custom_name(mock_ble):
    """Test BLE beacon initialization with custom name"""
    custom_name = "CustomBeacon"
    beacon = BleBeacon(name=custom_name)
    
    assert beacon.name == custom_name
    mock_ble.active.assert_called_once_with(True)

def test_ble_beacon_advertise(mock_ble):
    """Test BLE beacon advertisement"""
    beacon = BleBeacon(name="TestBeacon")
    beacon.advertise()
    
    # Verify advertisement was started with correct parameters
    mock_ble.gap_advertise.assert_called_once()
    args = mock_ble.gap_advertise.call_args[0]
    assert args[0] == 100000  # Check interval
    assert isinstance(args[1], bytes)  # Verify payload is bytes
    
    # Verify payload format (length byte + type byte + encoded name)
    payload = args[1]
    assert len(payload) == len("TestBeacon") + 2  # name length + 2 header bytes
    assert payload[0] == len("TestBeacon") + 1  # length byte includes type byte
    assert payload[1] == 0x09  # Complete Local Name type

def test_ble_beacon_stop(mock_ble):
    """Test stopping BLE advertisement"""
    beacon = BleBeacon()
    beacon.stop()
    
    # Verify advertisement was stopped with correct parameters
    mock_ble.gap_advertise.assert_called_once_with(0, None)

def test_ble_beacon_long_name(mock_ble):
    """Test BLE beacon with a long name (edge case)"""
    long_name = "VeryLongBeaconName" * 2  # 32 characters
    with pytest.raises(ValueError, match="Beacon name too long"):
        BleBeacon(name=long_name)

def test_ble_initialization_failure(mock_ble):
    """Test BLE initialization failure"""
    mock_ble.active.side_effect = Exception("BLE init failed")
    
    with pytest.raises(BLEError, match="Failed to initialize BLE"):
        BleBeacon()

def test_advertise_failure(mock_ble):
    """Test advertisement failure"""
    beacon = BleBeacon()
    mock_ble.gap_advertise.side_effect = Exception("Advertisement failed")
    
    with pytest.raises(BLEError, match="Failed to start advertising"):
        beacon.advertise()

def test_stop_failure(mock_ble):
    """Test stop advertisement failure"""
    beacon = BleBeacon()
    mock_ble.gap_advertise.side_effect = Exception("Stop failed")
    
    with pytest.raises(BLEError, match="Failed to stop advertising"):
        beacon.stop()