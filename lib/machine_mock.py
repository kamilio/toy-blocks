class Pin:
    OUT = 'out'
    
    def __init__(self, pin_id, mode=None):
        self._pin = pin_id
        self._mode = mode
        self._value = 0
        
    def value(self, val=None):
        if val is not None:
            self._value = val
        return self._value

class SPI:
    MSB = 'MSB'
    
    def __init__(self, id, **kwargs):
        self._id = id
        self._config = kwargs
        self._last_write = None
        
    def write(self, data):
        self._last_write = data
        return None
        
    def read(self, nbytes):
        # For testing, return a dummy status byte array
        result = bytes([0x55] * nbytes)
        # Make subscriptable for [0] access
        if nbytes == 1:
            return [result[0]]
        return result
