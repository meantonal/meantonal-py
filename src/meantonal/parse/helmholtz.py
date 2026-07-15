from __future__ import annotations

import re

from ..constants import LETTER_COORDS
from ..pitch import Pitch

_HELMHOLTZ_RE = re.compile(r"^([A-Ga-g])([#bxw]+)?((?:'|,)*)$")


class Helmholtz:
    """Helper class to parse Helmholtz pitch names into Pitch vectors or
    vice versa.
    """

    @staticmethod
    def to_pitch(s: str) -> Pitch:
        """Create a Pitch vector from a Helmholtz note name."""
        match = _HELMHOLTZ_RE.match(s)
        if not match:
            raise ValueError(f"Invalid Helmholtz string: {s}")

        letter, accidental_str, octave_str = match.groups()
        accidental_str = accidental_str or ""

        w, h = LETTER_COORDS["CDEFGAB".index(letter.upper())]

        accidental = 0
        accidental += accidental_str.count("#")
        accidental += 2 * accidental_str.count("x")
        accidental -= accidental_str.count("b")
        accidental -= 2 * accidental_str.count("w")
        w += accidental
        h -= accidental

        octave = 0
        if letter.isupper():
            octave = 3 - octave_str.count(",")
        if letter.islower():
            octave = 4 + octave_str.count("'")
        w += 5 * octave
        h += 2 * octave

        return Pitch(w, h)

    @staticmethod
    def from_pitch(p: Pitch) -> str:
        """Returns the Helmholtz note name of a Pitch.

        Raises ValueError if the Pitch's accidental is more than 8
        sharps/flats away from a natural, or its octave falls outside -3 to
        11 (a healthy margin beyond the range of human hearing). Both
        almost always indicate a logic error upstream.
        """
        acc_number = p.accidental
        if abs(acc_number) > 8:
            raise ValueError(
                f"Cannot render Helmholtz name: accidental ({acc_number}) "
                "exceeds the maximum of ±8 sharps/flats."
            )
        if p.octave < -3 or p.octave > 11:
            raise ValueError(
                f"Cannot render Helmholtz name: octave ({p.octave}) is "
                "outside the representable range (-3 to 11)."
            )

        accidental = ""
        if acc_number == 2:
            accidental += "x"
        elif acc_number > 0:
            accidental += "#" * acc_number
        if acc_number < 0:
            accidental += "b" * -acc_number

        octave = p.octave
        if octave > 2:
            return p.letter.lower() + accidental + "'" * (octave - 3)
        return p.letter + accidental + "," * (2 - octave)
