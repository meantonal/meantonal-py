from __future__ import annotations

from .map import Map2D

#: Used to map modes to numbers in certain methods.
MODES: dict[str, int] = {
    "LYDIAN": 0,
    "IONIAN": 1,
    "MIXOLYDIAN": 2,
    "DORIAN": 3,
    "AEOLIAN": 4,
    "PHRYGIAN": 5,
    "LOCRIAN": 6,
    "MAJOR": 1,
    "MINOR": 4,
}

#: Used in the construction of Pitch and Interval vectors by certain methods.
#: Each entry is a (w, h) pair, indexed C=0 .. B=6.
LETTER_COORDS: list[tuple[int, int]] = [
    (0, 0),  # C
    (1, 0),  # D
    (2, 0),  # E
    (2, 1),  # F
    (3, 1),  # G
    (4, 1),  # A
    (5, 1),  # B
]

WICKI_TO = Map2D(1, -3, 0, 1)
WICKI_FROM = Map2D(1, 3, 0, 1)
GENERATORS_TO = Map2D(2, -5, -1, 3)
GENERATORS_FROM = Map2D(3, 5, 1, 2)
