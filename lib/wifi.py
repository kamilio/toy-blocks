"""
Usage:
from logger import Logger

# With logging:
wifi = WiFi()
logger = Logger(prefix="WiFi", debug=True)
await wifi.connect(ssid="MyNetwork", password="MyPass")  # logs connection status

# With delay:
async def connect_wifi_with_delay():
    wifi = WiFi()
    if await wifi.connect():  # uses WIFI_SSID and WIFI_PASSWORD from wifi_config
        print(f"Connected to WiFi. IP: {wifi.get_ip()}")
    else:
        print("Failed to connect")

# Usage with gather:
# wifi = WiFi()
# await uasyncio.gather(
#     wifi.connect_with_delay(delay=5),
#     other_task(),
#     another_task()
# )
"""

import network
import uasyncio
from wifi_config import WIFI_SSID, WIFI_PASSWORD
from logger import Logger

class WiFi:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self._connected = False
        self.logger = Logger(prefix="WiFi", debug=True)
        
    async def connect(self, ssid = WIFI_SSID, password = WIFI_PASSWORD, timeout=20):
        if not self.wlan.isconnected():
            self.logger.info(f"Connecting to {ssid}...")
            self.wlan.connect(ssid, password)
            elapsed_seconds = 0
            last_status = None
            
            while True:
                if self.wlan.isconnected():
                    self.logger.info(f"Connected. IP: {self.get_ip()}")
                    self._connected = True
                    return True
                    
                if elapsed_seconds >= timeout:
                    self.wlan.disconnect()
                    self.logger.error(f"Connection timeout after {timeout}s")
                    return False
                
                status = self.wlan.status()
                if status != last_status:
                    status_name = {
                        network.STAT_IDLE: "IDLE",
                        network.STAT_CONNECTING: "CONNECTING",
                        network.STAT_WRONG_PASSWORD: "WRONG_PASSWORD",
                        network.STAT_NO_AP_FOUND: "NO_AP_FOUND",
                        # network.STAT_CONNECT_FAIL: "CONNECT_FAIL", 
                        network.STAT_GOT_IP: "GOT_IP"
                    }.get(status, f"Unknown status: {status}")
                    
                    self.logger.info(f"WiFi status: {status_name}")
                    last_status = status
                    
                    if status in [network.STAT_WRONG_PASSWORD, network.STAT_NO_AP_FOUND]:
                        self.wlan.disconnect()
                        return False
                    
                if elapsed_seconds % 2 == 0:  # Log every 2 seconds to avoid spam
                    self.logger.info(f"Still connecting... ({elapsed_seconds}s)")
                    
                await uasyncio.sleep(1)
                elapsed_seconds += 1
        
        return True
    
    async def disconnect(self):
        if self.wlan.isconnected():
            self.logger.info("Disconnecting from WiFi...")
            self.wlan.disconnect()
            while self.wlan.isconnected():
                await uasyncio.sleep(1)
            self._connected = False
            self.logger.info("Disconnected")
    
    def is_connected(self):
        return self.wlan.isconnected()
    
    def get_ip(self):
        if self.is_connected():
            return self.wlan.ifconfig()[0]
        return None
        
    async def connect_with_delay(self, delay=5, ssid=WIFI_SSID, password=WIFI_PASSWORD, timeout=20):
        self.logger.info(f"Waiting {delay}s before connecting...")
        await uasyncio.sleep(delay)
        return await self.connect(ssid, password, timeout)
