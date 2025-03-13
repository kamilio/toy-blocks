class Note:
    REST = 0
    C4 = 262
    CS4 = 277
    D4 = 294
    DS4 = 311
    E4 = 330
    F4 = 349
    FS4 = 370
    G4 = 392
    GS4 = 415
    A4 = 440
    AS4 = 466
    B4 = 494
    C5 = 523

    def __init__(self, value):
        self.value = value

    def __int__(self):
        return self.value
    
    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        return self.value == other.value
    
    @classmethod
    def from_int(cls, value):
        return cls(value)

class Duration:
    WHOLE = 1000
    HALF = 500
    QUARTER = 250
    EIGHTH = 125
    SIXTEENTH = 63
    THIRTYSECOND = 31

    def __init__(self, value):
        self.value = value

    def __int__(self):
        return self.value

    def __truediv__(self, other):
        return int(self) / other
    
    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        return self.value == other.value
    
    @classmethod
    def from_int(cls, value):
        return cls(value)