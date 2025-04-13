from lib.piezo_buzzer_types import Note, Duration

"""
Collection of songs for the piezo buzzer
Each song is a list of (note, duration) tuples specific to piezo buzzer usage
"""

COME_AS_YOU_ARE = [
    # First sequence
    (Note.D4, Duration.EIGHTH),
    (Note.D4, Duration.EIGHTH),
    (Note.E4, Duration.EIGHTH),
    (Note.FS4, Duration.EIGHTH),
    (Note.G4, Duration.EIGHTH),
    (Note.FS4, Duration.EIGHTH),
    (Note.FS4, Duration.EIGHTH),
    (Note.FS4, Duration.EIGHTH),
    
    # Second sequence
    (Note.FS4, Duration.EIGHTH),
    (Note.FS4, Duration.EIGHTH),
    (Note.E4, Duration.EIGHTH),
    (Note.D4, Duration.EIGHTH),
    (Note.D4, Duration.EIGHTH),
    (Note.D4, Duration.EIGHTH),
    (Note.D4, Duration.EIGHTH),
]

SMOKE_ON_THE_WATER = [
    (Note.D4, Duration.QUARTER),
    (Note.F4, Duration.HALF),
    (Note.G4, Duration.HALF),
    (Note.REST, Duration.QUARTER),
    
    (Note.D4, Duration.QUARTER),
    (Note.F4, Duration.HALF),
    (Note.GS4, Duration.HALF),
    (Note.G4, Duration.HALF),
    (Note.REST, Duration.QUARTER),
    
    (Note.D4, Duration.QUARTER),
    (Note.F4, Duration.HALF),
    (Note.G4, Duration.HALF),
    (Note.F4, Duration.HALF),
    (Note.D4, Duration.HALF)
]
