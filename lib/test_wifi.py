from wifi import WiFi
import pytest
import network
import uasyncio
from unittest.mock import MagicMock

@pytest.mark.asyncio
async def test_wifi_init():
    wifi = WiFi()
    wifi.wlan = MagicMock()
    wifi.wlan.active.return_value = True
    assert wifi.wlan.active()

@pytest.mark.asyncio
async def test_wifi_connect_success():
    wifi = WiFi()
    wifi.wlan = MagicMock()
    wifi.wlan.isconnected.return_value = True
    wifi.wlan.status.return_value = 3  # STAT_GOT_IP equivalent
    result = await wifi.connect("test_ssid", "test_pass")
    assert result == True
    assert wifi.is_connected()

@pytest.mark.asyncio
async def test_wifi_connect_timeout():
    wifi = WiFi()
    wifi.wlan = MagicMock()
    wifi.wlan.isconnected.return_value = False
    wifi.wlan.status.return_value = 1  # STAT_CONNECTING equivalent
    result = await wifi.connect("test_ssid", "test_pass", timeout=1)
    assert result == False
    assert not wifi.is_connected()

@pytest.mark.asyncio
async def test_wifi_disconnect():
    wifi = WiFi()
    wifi.wlan = MagicMock()
    # Mock successful connection
    wifi.wlan.isconnected.return_value = True
    await wifi.connect("test_ssid", "test_pass")
    # Mock successful disconnection
    wifi.wlan.isconnected.return_value = False
    await wifi.disconnect()
    assert not wifi.is_connected()

@pytest.mark.asyncio
async def test_get_ip():
    wifi = WiFi()
    wifi.wlan = MagicMock()
    wifi.wlan.isconnected.return_value = True
    wifi.wlan.ifconfig.return_value = ("192.168.1.100", "255.255.255.0", "192.168.1.1", "8.8.8.8")
    assert wifi.get_ip() == "192.168.1.100"

@pytest.mark.asyncio
async def test_get_ip_not_connected():
    wifi = WiFi()
    wifi.wlan = MagicMock()
    wifi.wlan.isconnected.return_value = False
    assert wifi.get_ip() is None