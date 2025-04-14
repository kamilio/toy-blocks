import os
import sys

# Add lib directory to Python path
lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.insert(0, lib_dir)

# Now we can import the mock modules
import bluetooth_mock  # noqa: E402
import hardware_mock  # noqa: E402
import network_mock  # noqa: E402
import time_mock  # noqa: E402
import uasyncio_mock  # noqa: E402
from pin_mock import MockPin, mock_pin  # noqa: E402, F401
from shift_register_mock import mock_shift_register  # noqa: E402, F401

# Get the necessary variables from the modules
mock_bluetooth = bluetooth_mock.mock_bluetooth
mock_machine = hardware_mock.mock_machine
mock_network = network_mock.mock_network
mock_urequests = network_mock.mock_urequests
mock_const = time_mock.mock_const
mock_time = time_mock.mock_time
mock_uasyncio = uasyncio_mock.mock_uasyncio

# Set up mock modules in sys.modules
mock_micropython = mock_machine  # reuse machine mock for micropython
mock_micropython.const = mock_const
sys.modules['micropython'] = mock_micropython
sys.modules['machine'] = mock_machine
sys.modules['bluetooth'] = mock_bluetooth
sys.modules['network'] = mock_network
sys.modules['urequests'] = mock_urequests
sys.modules['uasyncio'] = mock_uasyncio
sys.modules['time'] = mock_time
