import network
import uasyncio

class WiFi:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        self._connected = False
        
    async def connect(self, ssid, password, timeout=10):
        if not self.wlan.isconnected():
            self.wlan.connect(ssid, password)
            elapsed_seconds = 0
            
            while True:
                if self.wlan.isconnected():
                    self._connected = True
                    return True
                    
                if elapsed_seconds >= timeout:
                    self.wlan.disconnect()
                    return False
                    
                await uasyncio.sleep(1)
                elapsed_seconds += 1
        
        return True
    
    async def disconnect(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
            while self.wlan.isconnected():
                await uasyncio.sleep(1)
            self._connected = False
    
    def is_connected(self):
        return self.wlan.isconnected()
    
    def get_ip(self):
        if self.is_connected():
            return self.wlan.ifconfig()[0]
        return None