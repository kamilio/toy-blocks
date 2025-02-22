from micropython import const
import bluetooth
import struct
import time

# Constants
_ADV_TYPE_NAME = const(0x09)
_ADV_INTERVAL_US = const(100000)  # 100ms
_MAX_ADV_DATA_LEN = const(31)

class BLEError(Exception):
    """Custom exception for BLE-related errors"""
    pass

class BleBeacon:
    def __init__(self, name="MyBeacon"):
        if len(name) > _MAX_ADV_DATA_LEN - 2:  # Account for length and type bytes
            raise ValueError("Beacon name too long")
            
        try:
            self.ble = bluetooth.BLE()
            self.ble.active(True)
            self.name = name
        except Exception as e:
            raise BLEError(f"Failed to initialize BLE: {str(e)}")
        
    def advertise(self):
        try:
            # Construct advertisement payload
            payload = struct.pack("BB", len(self.name) + 1, _ADV_TYPE_NAME) + self.name.encode()
            
            if len(payload) > _MAX_ADV_DATA_LEN:
                raise ValueError("Advertisement payload too long")
            
            # Start advertising
            # MicroPython BLE API: gap_advertise(interval_us, data)
            self.ble.gap_advertise(_ADV_INTERVAL_US, payload)
        except Exception as e:
            raise BLEError(f"Failed to start advertising: {str(e)}")
    
    def stop(self):
        try:
            # Stop advertising by setting interval to 0
            self.ble.gap_advertise(0, None)
        except Exception as e:
            raise BLEError(f"Failed to stop advertising: {str(e)}")

# Usage
# beacon = BleBeacon("ConfigTrigger")
# beacon.advertise()