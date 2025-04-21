from unittest.mock import MagicMock, patch

from lib.power_cycle_detector import PowerCycleDetector
from lib.time_mock import mock_time, set_time


class TestPowerCycleDetector:
    def setup_method(self):
        set_time(0)
        self.rtc_mock = MagicMock()
        self.rtc_memory = bytearray([0] * 5)
        self.rtc_mock.return_value.memory.side_effect = self.mock_memory
        self.rtc_patcher = patch('machine.RTC', self.rtc_mock)
        self.time_patcher = patch('lib.power_cycle_detector.time', mock_time)
        self.rtc_patcher.start()
        self.time_patcher.start()

    def teardown_method(self):
        self.rtc_patcher.stop()
        self.time_patcher.stop()

    def mock_memory(self, value=None):
        if value is not None:
            self.rtc_memory[:] = value
            return None
        return self.rtc_memory

    def test_initialization_fresh(self):
        detector = PowerCycleDetector()
        assert detector.boot_count == 0
        assert detector.last_boot_time == 0
        assert detector.cycles_threshold == 3
        assert detector.time_window_ms == 5000

    def test_initialization_with_custom_params(self):
        detector = PowerCycleDetector(cycles_threshold=5, time_window_ms=10000)
        assert detector.cycles_threshold == 5
        assert detector.time_window_ms == 10000

    def test_initialization_with_existing_data(self):
        self.rtc_memory = bytearray([2, 0, 0, 3, 232])  # boot count 2, time 1000
        detector = PowerCycleDetector()
        assert detector.boot_count == 2
        assert detector.last_boot_time == 1000

    def test_update_boot_sequence_first_boot(self):
        detector = PowerCycleDetector()
        set_time(1000 * 1000)  # Convert to microseconds
        detector.update_boot_sequence()

        assert detector.boot_count == 1
        assert detector.last_boot_time == 1000

    def test_update_boot_sequence_rapid_boots(self):
        detector = PowerCycleDetector()

        # First boot
        set_time(1000 * 1000)
        detector.update_boot_sequence()
        assert detector.boot_count == 1

        # Second boot within window
        set_time(2000 * 1000)
        detector.update_boot_sequence()
        assert detector.boot_count == 2

        # Third boot within window
        set_time(3000 * 1000)
        detector.update_boot_sequence()
        assert detector.boot_count == 3
        assert detector.is_rapid_boot_sequence()

    def test_update_boot_sequence_delayed_boot(self):
        detector = PowerCycleDetector()

        # First boot
        set_time(1000 * 1000)
        detector.update_boot_sequence()
        assert detector.boot_count == 1

        # Second boot outside window
        set_time(7000 * 1000)
        detector.update_boot_sequence()
        assert detector.boot_count == 1  # Should reset to 1
        assert not detector.is_rapid_boot_sequence()

    def test_update_boot_sequence_edge_cases(self):
        detector = PowerCycleDetector(time_window_ms=5000)

        # First boot
        set_time(1000 * 1000)
        detector.update_boot_sequence()

        # Boot exactly at window boundary
        set_time(6000 * 1000)  # 5000ms after first boot
        detector.update_boot_sequence()
        assert detector.boot_count == 1  # Should reset as it's at boundary

    def test_is_rapid_boot_sequence_threshold(self):
        detector = PowerCycleDetector(cycles_threshold=3)

        for i in range(1, 4):
            set_time(i * 1000 * 1000)
            detector.update_boot_sequence()
            if i < 3:
                assert not detector.is_rapid_boot_sequence()
            else:
                assert detector.is_rapid_boot_sequence()

    def test_reset_sequence(self):
        detector = PowerCycleDetector()

        # Simulate rapid boots
        for i in range(3):
            set_time(i * 1000 * 1000)
            detector.update_boot_sequence()

        assert detector.is_rapid_boot_sequence()

        set_time(4000 * 1000)
        detector.reset_sequence()

        assert detector.boot_count == 0
        assert detector.last_boot_time == 4000
        assert not detector.is_rapid_boot_sequence()

    def test_memory_persistence(self):
        detector = PowerCycleDetector()

        set_time(1000 * 1000)
        detector.update_boot_sequence()

        assert self.rtc_memory[0] == 1  # boot_count
        assert int.from_bytes(self.rtc_memory[1:5], 'big') == 1000  # last_boot_time
