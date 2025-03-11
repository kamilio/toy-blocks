class Logger:
    def __init__(self, prefix="", debug=False):
        self.debug = debug
        self.prefix = prefix
        
    def _log(self, message):
        if not self.debug:
            return
        
        print(f"[{self.prefix}] {message}")
            
    def info(self, message):
        self._log(message)
        
    def error(self, message):
        self._log(f"ERROR: {message}")