import sys
import os

# Add lib directory to Python path
lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
sys.path.insert(0, lib_dir)

from time_mock import (
    mock_current_time, advance_time, mock_const, mock_time,
    reset_time
)

from pin_mock import (
    MockPin,
    mock_pin
)

from hardware_mock import (
    MockRTC,
    mock_machine
)

from bluetooth_mock import (
    MockBLE,
    mock_bluetooth
)

from network_mock import (
    MockWLAN,
    MockResponse,
    mock_network,
    mock_urequests,
    mock_get
)

from shift_register_mock import (
    MockShiftRegister,
    ShiftRegisterLed,
    mock_shift_register
)

from uasyncio_mock import (
    mock_sleep,
    mock_create_task,
    mock_uasyncio
)

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
