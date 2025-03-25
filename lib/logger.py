import sys
import time

class Logger:
    def __init__(self, prefix="", debug=False):
        self.debug = debug
        self.prefix = prefix
        self._last_log = 0
        self._log_threshold = 0.1  # seconds between logs
        
    def _log(self, message):
        if not self.debug:
            return
            
        current_time = time.time()
        if current_time - self._last_log < self._log_threshold:
            return
            
        self._last_log = current_time
        
        try:
            print(f"[{self.prefix}] {message}")
        except:
            pass
            
    def info(self, message):
        self._log(message)
        
    def error(self, message):
        self._log(f"ERROR: {message}")

    def set_threshold(self, seconds):
        self._log_threshold = seconds