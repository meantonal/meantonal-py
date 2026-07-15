from __future__ import annotations

import re

from ..constants import LETTER_COORDS
from ..pitch import Pitch

_ABC_RE = re.compile(r"^([_=^]+)?([A-Ga-g])((?:'|,)*)$")


class ABC:
    """Helper class to parse ABC notation into Pitch vectors or vice versa."""

    @staticmethod
    def to_pitch(s: str) -> Pitch:
        """Create a Pitch vector from an ABC note name."""
        match = _ABC_RE.match(s)
        if not match:
            raise ValueError(f"Invalid ABC string: {s}")

        accidental_str, letter, octave_str = match.groups()
        accidental_str = accidental_str or ""

        w, h = LETTER_COORDS["CDEFGAB".index(letter.upper())]

        accidental = 0
        accidental += accidental_str.count("^")
        accidental -= accidental_str.count("_")
        w += accidental
        h -= accidental

        octave = 0
        if letter.isupper():
            octave = 5 - octave_str.count(",")
        if letter.islower():
            octave = 6 + octave_str.count("'")
        w += 5 * octave
        h += 2 * octave

        return Pitch(w, h)

    @staticmethod
    def from_pitch(p: Pitch) -> str:
        """Returns the ABC note name of a Pitch vector.

        Raises ValueError if the Pitch's accidental goes beyond a double
        sharp/flat, or its octave falls outside -3 to 11 (a healthy margin
        beyond the range of human hearing). ABC notation has no provision
        for anything beyond a double sharp/flat, and both almost always
        indicate a logic error upstream.
        """
        acc_number = p.accidental
        if abs(acc_number) > 2:
            raise ValueError(
                f"Cannot render ABC name: accidental ({acc_number}) exceeds "
                "the double sharp/flat limit (±2)."
            )
        if p.octave < -3 or p.octave > 11:
            raise ValueError(
                f"Cannot render ABC name: octave ({p.octave}) is outside "
                "the representable range (-3 to 11)."
            )

        accidental = ""
        if acc_number > 0:
            accidental += "^" * acc_number
        if acc_number < 0:
            accidental += "_" * -acc_number

        octave = p.octave
        if octave > 4:
            return accidental + p.letter.lower() + "'" * (octave - 5)
        return accidental + p.letter.upper() + "," * (4 - octave)
