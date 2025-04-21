Here are the main time-related functions in MicroPython for ESP32:

**Core timing functions:**
- `time.ticks_ms()` - Returns millisecond counter with arbitrary reference point
- `time.ticks_us()` - Returns microsecond counter
- `time.ticks_cpu()` - Returns CPU cycle counter
- `time.ticks_diff(t2, t1)` - Measures period between timestamps
- `time.ticks_add(ticks, delta)` - Adds a delta to a timestamp

**Sleep functions:**
- `time.sleep(seconds)` - Sleep for specified number of seconds
- `time.sleep_ms(ms)` - Sleep for specified number of milliseconds
- `time.sleep_us(us)` - Sleep for specified number of microseconds

**Other time functions:**
- `time.time()` - Returns seconds since epoch if RTC is set
- `time.localtime([secs])` - Convert seconds since epoch to 8-tuple format
- `time.mktime(tuple)` - Convert 8-tuple format to seconds since epoch

The ticks functions are particularly useful for timing operations and creating delays without blocking execution completely.