from __future__ import annotations

import re

from ..constants import LETTER_COORDS
from ..pitch import Pitch

_SPN_RE = re.compile(r"^([A-Ga-g])([#bxw]+)?(-?\d+)$")


class SPN:
    """Helper class to parse Scientific Pitch Notation to Pitch vectors or
    vice versa.
    """

    @staticmethod
    def to_pitch(spn: str) -> Pitch:
        """Create a Pitch vector from a Scientific Pitch Notation string."""
        match = _SPN_RE.match(spn)
        if not match:
            raise ValueError(f"Invalid SPN: {spn}")

        letter, accidental_str, octave_str = match.groups()
        accidental_str = accidental_str or ""
        octave = int(octave_str) + 1

        w, h = LETTER_COORDS["CDEFGAB".index(letter.upper())]

        accidental = 0
        accidental += accidental_str.count("#")
        accidental += 2 * accidental_str.count("x")
        accidental -= accidental_str.count("b")
        accidental -= 2 * accidental_str.count("w")

        w += accidental
        h -= accidental
        w += 5 * octave
        h += 2 * octave

        return Pitch(w, h)

    @staticmethod
    def from_pitch(p: Pitch) -> str:
        """Returns the SPN name of a Pitch.

        Raises ValueError if the Pitch's accidental is altered by more than
        8 sharps/flats, which is chosen as an arbitrary limit simply to
        avoid handling strings of unbounded size, and because it almost
        always indicates a logic error upstream.
        """
        accidental = p.accidental
        if abs(accidental) > 8:
            raise ValueError(
                f"Cannot render SPN name: accidental ({accidental}) exceeds "
                "the maximum of ±8 sharps/flats."
            )

        result = p.letter

        if accidental == 2:
            result += "x"
        elif accidental > 0:
            result += "#" * accidental
        if accidental < 0:
            result += "b" * -accidental

        result += str(p.octave)

        return result
