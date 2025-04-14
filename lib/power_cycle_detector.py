import time

import machine


class PowerCycleDetector:
    def __init__(self, cycles_threshold=3, time_window_ms=5000):
        self.rtc = machine.RTC()
        self.cycles_threshold = cycles_threshold
        self.time_window_ms = time_window_ms

        try:
            self.boot_count = self.rtc.memory()[0]
            self.last_boot_time = int.from_bytes(self.rtc.memory()[1:5], 'big')
        except Exception:
            self.boot_count = 0
            self.last_boot_time = 0

    def update_boot_sequence(self) -> None:
        """
        Updates and stores boot sequence information in RTC memory.
        Should be called early in the boot process.
        """
        current_time = time.ticks_ms()

        if time.ticks_diff(current_time, self.last_boot_time) < self.time_window_ms:
            self.boot_count += 1
        else:
            self.boot_count = 1

        # Store updated values in RTC memory
        self.rtc.memory(bytes([self.boot_count]) + current_time.to_bytes(4, 'big'))
        self.last_boot_time = current_time

    def is_rapid_boot_sequence(self) -> bool:
        """
        Returns True if the device has been power cycled rapidly
        enough times to exceed the threshold.
        """
        return self.boot_count >= self.cycles_threshold

    def reset_sequence(self) -> None:
        """
        Resets the boot sequence counter. Call this after handling the rapid boot sequence.
        """
        self.boot_count = 0
        current_time = time.ticks_ms()
        self.rtc.memory(bytes([self.boot_count]) + current_time.to_bytes(4, 'big'))
        self.last_boot_time = current_time
