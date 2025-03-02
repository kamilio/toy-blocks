from enum import IntEnum

class Note(IntEnum):
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

class Duration(IntEnum):
    WHOLE = 1000
    HALF = 500
    QUARTER = 250
    EIGHTH = 125
    SIXTEENTH = 63
    THIRTYSECOND = 31