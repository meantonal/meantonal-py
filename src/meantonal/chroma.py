from __future__ import annotations

import math


class Chroma:
    """Contains some static helper methods for extracting information from
    "chroma", the signed distance of a Pitch from C or an Interval from the
    unison in perfect 5ths.
    """

    @staticmethod
    def to_letter(chroma: int) -> str:
        """Returns the letter component of the pitch class name represented
        by a given Pitch chroma.
        """
        return "CDEFGAB"[((chroma * 4) % 7 + 7) % 7]

    @staticmethod
    def to_accidental(chroma: int) -> int:
        """Returns the accidental component of the pitch class name
        represented by a given Pitch chroma.

        - 0 is natural.
        - +1 / -1 is sharp/flat.
        - +2 / -2 is double sharp/double flat.

        etc. for arbitrarily remote accidentals.
        """
        return math.floor((chroma + 1) / 7)
