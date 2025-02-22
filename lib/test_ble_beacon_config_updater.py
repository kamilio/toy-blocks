import unittest
from unittest.mock import MagicMock, patch, mock_open
from ble_beacon_config_updater import SimpleConfigUpdater
import json

class TestSimpleConfigUpdater(unittest.TestCase):
    def setUp(self):
        self.updater = SimpleConfigUpdater(
            target_beacon_name="TestBeacon",
            ssid="test_wifi",
            password="test_pass",
            config_url="http://test.com/config.json"
        )
        
    def test_init(self):
        """Test initialization with custom parameters"""
        self.assertEqual(self.updater.target_beacon, "TestBeacon")
        self.assertEqual(self.updater.ssid, "test_wifi")
        self.assertEqual(self.updater.password, "test_pass")
        self.assertEqual(self.updater.config_url, "http://test.com/config.json")
        self.assertFalse(self.updater.device_found)

    def test_ble_scan_callback_valid_device(self):
        """Test BLE scan callback with valid device"""
        # Simulate finding target device with good RSSI
        test_data = (0, bytes([1, 2, 3, 4, 5, 6]), 0, -60, 
                    bytes("TestBeacon".encode()))
        self.updater.ble_scan_callback(5, test_data)
        self.assertTrue(self.updater.device_found)

    def test_ble_scan_callback_weak_signal(self):
        """Test BLE scan callback with weak signal"""
        # Simulate finding target device with weak RSSI
        test_data = (0, bytes([1, 2, 3, 4, 5, 6]), 0, -80, 
                    bytes("TestBeacon".encode()))
        self.updater.ble_scan_callback(5, test_data)
        self.assertFalse(self.updater.device_found)

    def test_ble_scan_callback_wrong_name(self):
        """Test BLE scan callback with wrong device name"""
        test_data = (0, bytes([1, 2, 3, 4, 5, 6]), 0, -60, 
                    bytes("WrongBeacon".encode()))
        self.updater.ble_scan_callback(5, test_data)
        self.assertFalse(self.updater.device_found)

    @patch('network.WLAN')
    @patch('urequests.get')
    def test_update_config_success(self, mock_get, mock_wlan):
        """Test successful config update process"""
        # Mock check_for_trigger to return True
        self.updater.check_for_trigger = MagicMock(return_value=True)
        
        # Mock WLAN connection
        mock_wlan_instance = MagicMock()
        mock_wlan_instance.isconnected.return_value = True
        mock_wlan.return_value = mock_wlan_instance
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"test": "config"}
        mock_get.return_value = mock_response
        
        # Mock file operations
        m = mock_open()
        with patch('builtins.open', m):
            result = self.updater.update_config()
        
        self.assertTrue(result)
        mock_wlan_instance.connect.assert_called_once_with(
            self.updater.ssid, self.updater.password)
        mock_get.assert_called_once_with(self.updater.config_url)
        self.assertTrue(m().write.call_count > 0)  # json.dump writes characters individually

    @patch('network.WLAN')
    def test_update_config_wifi_failure(self, mock_wlan):
        """Test config update with WiFi connection failure"""
        # Mock check_for_trigger to return True
        self.updater.check_for_trigger = MagicMock(return_value=True)
        
        # Mock WLAN connection failure
        mock_wlan_instance = MagicMock()
        mock_wlan_instance.isconnected.return_value = False
        mock_wlan.return_value = mock_wlan_instance
        
        result = self.updater.update_config()
        
        self.assertFalse(result)
        mock_wlan_instance.connect.assert_called_once_with(
            self.updater.ssid, self.updater.password)
        mock_wlan_instance.disconnect.assert_called_once()

    def test_check_for_trigger(self):
        """Test BLE scanning for trigger device"""
        # Mock BLE methods
        self.updater.ble.gap_scan = MagicMock()
        self.updater.ble.irq = MagicMock()
        self.updater.device_found = False
        
        result = self.updater.check_for_trigger()
        
        self.assertFalse(result)
        self.updater.ble.gap_scan.assert_called_once_with(2000, 30000, 30000)
        self.assertEqual(self.updater.ble.irq.call_count, 2)  # Called once to set and once to clear

if __name__ == '__main__':
    unittest.main()