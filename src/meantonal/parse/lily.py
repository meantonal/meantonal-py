from __future__ import annotations

import re

from ..constants import LETTER_COORDS
from ..pitch import Pitch

_LILY_RE = re.compile(r"^([a-g])((?:is|es)*)((?:'|,)*)$")


def _parse_accidental(accidental_str: str) -> int:
    accidental = 0
    for token in re.findall("is|es", accidental_str):
        if token == "is":
            accidental += 1
        else:
            accidental -= 1
    return accidental


class LilyPond:
    """Helper class to parse LilyPond note names into Pitch vectors or vice
    versa.
    """

    @staticmethod
    def to_pitch(s: str) -> Pitch:
        """Create a Pitch vector from a LilyPond note name."""
        match = _LILY_RE.match(s)
        if not match:
            raise ValueError(f"Invalid LilyPond note name: {s}")

        letter, accidental_str, octave_str = match.groups()

        accidental = _parse_accidental(accidental_str)

        octave = 4 + octave_str.count("'") - octave_str.count(",")

        w, h = LETTER_COORDS["cdefgab".index(letter)]
        w += accidental
        h -= accidental
        w += 5 * octave
        h += 2 * octave

        return Pitch(w, h)

    @staticmethod
    def from_pitch(p: Pitch) -> str:
        """Returns the (absolute) LilyPond name of a Pitch.

        Raises ValueError if the Pitch's accidental goes beyond a double
        sharp/flat, or its octave falls outside -3 to 11 (a healthy margin
        beyond the range of human hearing). Neither is representable in
        real LilyPond input, and both almost always indicate a logic error
        upstream.
        """
        accidental = p.accidental
        if abs(accidental) > 2:
            raise ValueError(
                f"Cannot render LilyPond name: accidental ({accidental}) "
                "exceeds the double sharp/flat limit (±2)."
            )
        if p.octave < -3 or p.octave > 11:
            raise ValueError(
                f"Cannot render LilyPond name: octave ({p.octave}) is "
                "outside the representable range (-3 to 11)."
            )

        result = p.letter.lower()

        if accidental > 0:
            result += "is" * accidental
        if accidental < 0:
            result += "es" * -accidental

        octave = p.octave - 3
        if octave > 0:
            result += "'" * octave
        if octave < 0:
            result += "," * -octave

        return result

    @staticmethod
    def relative(start: Pitch) -> _RelativeParser:
        return _RelativeParser(start)


class _RelativeParser:
    """Parses LilyPond note names in relative-octave mode, where each note's
    octave is inferred from its distance to the previously parsed pitch.

    Not part of the public API directly -- reached only via
    LilyPond.relative(start).
    """

    def __init__(self, start: Pitch) -> None:
        self._previous = start

    def to_pitch(self, s: str) -> Pitch:
        match = _LILY_RE.match(s)
        if not match:
            raise ValueError(f"Invalid LilyPond note name: {s}")

        letter, accidental_str, octave_str = match.groups()

        accidental = _parse_accidental(accidental_str)

        w, h = LETTER_COORDS["cdefgab".index(letter)]
        w += accidental
        h -= accidental

        result = Pitch(w, h)

        while result.interval_to(self._previous).stepspan > 3:
            result.w += 5
            result.h += 2
        while result.interval_to(self._previous).stepspan < -3:
            result.w -= 5
            result.h -= 2

        octave = octave_str.count("'") - octave_str.count(",")
        result.w += 5 * octave
        result.h += 2 * octave

        self._previous = Pitch(result.w, result.h)

        return result
