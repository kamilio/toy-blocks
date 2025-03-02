from wifi import WiFi
import pytest
from unittest.mock import patch
import uasyncio

@pytest.mark.asyncio
async def test_wifi_init():
    wifi = WiFi()
    assert wifi.wlan.active()

@pytest.mark.asyncio
async def test_wifi_connect_success():
    wifi = WiFi()
    result = await wifi.connect("test_ssid", "test_pass")
    assert result == True
    assert wifi.is_connected()

@pytest.mark.asyncio
async def test_wifi_connect_timeout():
    wifi = WiFi()
    wifi.wlan.isconnected = lambda: False
    result = await wifi.connect("test_ssid", "test_pass", timeout=1)
    assert result == False
    assert not wifi.is_connected()

@pytest.mark.asyncio
async def test_wifi_disconnect():
    wifi = WiFi()
    await wifi.connect("test_ssid", "test_pass")
    await wifi.disconnect()
    assert not wifi.is_connected()

@pytest.mark.asyncio
async def test_get_ip():
    wifi = WiFi()
    await wifi.connect("test_ssid", "test_pass")
    assert wifi.get_ip() is not None

@pytest.mark.asyncio
async def test_get_ip_not_connected():
    wifi = WiFi()
    assert wifi.get_ip() is None