from __future__ import annotations

import math
import re
from typing import NamedTuple

from .chroma import Chroma
from .constants import LETTER_COORDS, MODES
from .pitch import Pitch

_TONIC_RE = re.compile(r"^([A-Ga-g])([#bxw]+)?$")
_ACCIDENTAL_MAP: dict[str, int] = {"#": 1, "x": 2, "b": -1, "w": -2}


def _js_mod(a: int, b: int) -> int:
    """Mimics JavaScript's % operator, which (unlike Python's) takes the
    sign of the dividend rather than the divisor -- needed for
    TonalContext.degree_chroma, which (unlike most other modulo use in this
    library) relies on the raw signed result rather than a canonicalized
    non-negative one.
    """
    return int(math.fmod(a, b))


class _Tonic(NamedTuple):
    letter: str
    accidental: int
    chroma: int


class TonalContext:
    """Stores information about the currently governing key or mode.

    - It is used with various methods to query or transform the position of
      Pitch vectors within a key or mode.
    - Created from the "chroma" of the tonic scale degree (its signed
      distance from C in perfect fifths), and the mode, numbered in
      ascending 5ths from Lydian = 0.
    - Can also be created from strings with TonalContext.from_strings()
    """

    tonic: _Tonic
    mode: int

    def __init__(self, chroma: int, mode: int) -> None:
        self.tonic = _Tonic(
            letter=Chroma.to_letter(chroma),
            accidental=Chroma.to_accidental(chroma),
            chroma=chroma,
        )
        self.mode = mode
        self._chroma_offset = mode - chroma

    @classmethod
    def from_strings(cls, tonic: str, mode: str) -> TonalContext:
        """Create a TonalContext using two strings for the tonic note name
        and the mode.

        - e.g. TonalContext.from_strings("C#", "Dorian")
        """
        match = _TONIC_RE.match(tonic)
        if not match:
            raise ValueError(f"Invalid tonic string: {tonic}")

        mode_number = MODES.get(mode.upper())
        if mode_number is None:
            raise ValueError(f"Invalid mode string: {mode}")

        letter, accidental_str = match.groups()
        accidental_str = accidental_str or ""
        w, h = LETTER_COORDS["CDEFGAB".index(letter.upper())]

        for char in accidental_str:
            delta = _ACCIDENTAL_MAP.get(char, 0)
            w += delta
            h -= delta
        chroma = 2 * w - 5 * h

        return cls(chroma, mode_number)

    def degree_number(self, p: Pitch) -> int:
        """Returns the scale degree (0-indexed) of the passed in Pitch
        vector in the current context.
        """
        return (p.w + p.h - "CDEFGAB".index(self.tonic.letter)) % 7

    def degree_alteration(self, p: Pitch) -> int:
        """Returns the scale degree alteration represented by a Pitch in the
        current TonalContext, e.g. C# is a raised note in the key of C
        major.

        0 represents a diatonic Pitch.
        +1 / -1 represent a Pitch raised/lowered with accidentals.
        +2 / -2 represent Pitches too remote to belong in a given
        TonalContext.
        """
        x = p.chroma + self._chroma_offset
        if 0 <= x < 7:
            return 0
        if 7 <= x < 12:
            return 1
        if -5 <= x < 0:
            return -1
        if x < -5:
            return -2
        return 2

    def degree_chroma(self, degree: int, alteration: int = 0) -> int:
        """Returns the chroma (signed distance in perfect 5ths from C) of
        the variant of the passed in scale degree (0-indexed so the tonic
        is 0) that matches the specified alteration (or diatonic if
        unspecified).

        Note: this method doesn't enforce the 17-fifths window used to
        define keys, and will happily produce a degree altered by 4
        chromatic semitones.
        """
        return (
            _js_mod(degree * 2 + self.mode, 7)
            + alteration * 7
            - self._chroma_offset
        )

    def snap_diatonic(self, p: Pitch) -> Pitch:
        """Snaps a Pitch vector to the diatonic position for that
        letter-name in the current TonalContext.

        - e.g. in D major, F4 would "snap" to F#4.
        """
        result = Pitch(p.w, p.h)
        while result.alteration_in(self) > 0:
            result.w -= 1
            result.h += 1
        while result.alteration_in(self) < 0:
            result.w += 1
            result.h -= 1

        return result
