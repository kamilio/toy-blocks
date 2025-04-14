from unittest.mock import MagicMock


class MockWLAN:
    STA_IF = 1

    def __init__(self, interface):
        self._active = False
        self._connected = False

    def active(self, state=None):
        if state is not None:
            self._active = state
        return self._active

    def isconnected(self):
        return self._connected

    def connect(self, ssid, password):
        self._connected = True

    def disconnect(self):
        self._connected = False

    def ifconfig(self):
        return ('192.168.1.100', '255.255.255.0', '192.168.1.1', '8.8.8.8')


class MockResponse:
    def __init__(self, json_data):
        self._json_data = json_data

    def json(self):
        return self._json_data

    def close(self):
        pass


def mock_get(url):
    return MockResponse({'test': 'config'})


# Mock network module
mock_network = MagicMock()
mock_network.WLAN = MockWLAN

# Mock urequests module
mock_urequests = MagicMock()
mock_urequests.get = mock_get
