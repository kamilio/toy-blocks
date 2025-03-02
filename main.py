# main.py runs after boot.py and is meant for:
# - Your main application code
# - Program logic
# - Sleep/shutdown functions

import machine
import uasyncio
from auto_shutdown import AutoShutdown
from debug_led import DebugLed
from wifi import WiFi

WIFI_SSID = "your_ssid"        # Replace with your WiFi network name
WIFI_PASSWORD = "your_pass"     # Replace with your WiFi password

auto_shutdown = AutoShutdown(timeout=600)
debug = DebugLed()
wifi = WiFi()

async def setup_wifi():
    print("[WiFi] Connecting to network...")
    if await wifi.connect(WIFI_SSID, WIFI_PASSWORD):
        print("[WiFi] Connected successfully")
        print("[WiFi] IP:", wifi.get_ip())
        return True
    print("[WiFi] Connection failed")
    return False

async def main():
    print("[Main] Starting application...")
    await debug.blink(5)
    debug.on()
    
    if await setup_wifi():
        print("[Main] WiFi setup complete")
    else:
        print("[Main] WiFi setup failed")
        await debug.blink(3)  # Error indication
    
    while True:
        await uasyncio.sleep(0.1)
        auto_shutdown.maybe_deepsleep()
        if not wifi.is_connected():
            print("[WiFi] Connection lost, attempting to reconnect...")
            await setup_wifi()

uasyncio.run(main())