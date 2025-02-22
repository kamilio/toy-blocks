from machine import Pin
import network
import bluetooth
import urequests
import json
import time

class SimpleConfigUpdater:
    """
    A class to update device configuration based on BLE beacon triggers.
    
    This class scans for a specific BLE beacon and when found, connects to WiFi
    to download and update the device's configuration from a remote server.
    """
    
    def __init__(self, target_beacon_name="ConfigTrigger", 
                 ssid="YOUR_WIFI", password="YOUR_PASS",
                 config_url="http://your-server.com/config.json",
                 min_rssi=-70):
        """
        Initialize the config updater.
        
        Args:
            target_beacon_name (str): Name of the beacon to trigger updates
            ssid (str): WiFi network name
            password (str): WiFi password
            config_url (str): URL to fetch new configuration from
            min_rssi (int): Minimum signal strength to consider beacon (-70 default)
        """
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        self.target_beacon = target_beacon_name
        self.device_found = False
        self.min_rssi = min_rssi
        
        # WiFi settings
        self.ssid = ssid
        self.password = password
        self.config_url = config_url
    
    def ble_scan_callback(self, event, data):
        """
        Callback function for BLE scan events.
        
        Args:
            event (int): Event type (5 for scan result)
            data (tuple): Scan result data containing device information
        """
        if event == 5:  # scan result
            addr_type, addr, adv_type, rssi, adv_data = data
            try:
                # Try to decode the name from advertising data
                name = bytes(adv_data).decode()
                if self.target_beacon in name and rssi > self.min_rssi:
                    self.device_found = True
            except (UnicodeError, AttributeError) as e:
                # Ignore decoding errors for non-matching devices
                pass
    
    def check_for_trigger(self):
        """
        Scan for the trigger beacon device.
        
        Returns:
            bool: True if trigger device was found, False otherwise
        """
        self.device_found = False
        self.ble.irq(self.ble_scan_callback)
        self.ble.gap_scan(2000, 30000, 30000)  # Scan for 2 seconds
        time.sleep(2)
        self.ble.irq(lambda event, data: None)  # Safe way to clear IRQ
        return self.device_found
    
    def update_config(self):
        """
        Attempt to update configuration if trigger beacon is found.
        
        This method will:
        1. Check for trigger beacon
        2. Connect to WiFi if beacon found
        3. Download new configuration
        4. Save configuration to file
        5. Cleanup connections
        
        Returns:
            bool: True if config was updated successfully, False otherwise
        """
        wlan = None
        try:
            if not self.check_for_trigger():
                return False
                
            print("Trigger beacon found")
            
            # Connect to WiFi
            wlan = network.WLAN(network.STA_IF)
            wlan.active(True)
            wlan.connect(self.ssid, self.password)
            
            # Wait for connection
            timeout = 10
            while not wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            if not wlan.isconnected():
                raise ConnectionError("Failed to connect to WiFi")
            
            # Download new config
            response = urequests.get(self.config_url)
            try:
                new_config = response.json()
                
                # Save config
                with open('config.json', 'w') as f:
                    json.dump(new_config, f)
                
                print("Config updated successfully")
                return True
                
            finally:
                response.close()
                
        except ConnectionError as e:
            print(f"Connection error: {str(e)}")
        except OSError as e:
            print(f"OS error: {str(e)}")
        except ValueError as e:
            print(f"Value error (likely JSON related): {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
        finally:
            if wlan:
                try:
                    wlan.disconnect()
                except:
                    pass
        
        return False

# # Usage
# def main():
#     updater = SimpleConfigUpdater(
#         target_beacon_name="ConfigTrigger",
#         ssid="your_wifi_name",
#         password="your_wifi_password",
#         config_url="http://your-server.com/config.json"
#     )
#     
#     while True:
#         if updater.update_config():
#             # Config updated, maybe restart
#             print("New config applied")
#         time.sleep(10)  # Check every 10 seconds