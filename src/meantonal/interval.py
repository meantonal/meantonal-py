from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Iterator, Optional

if TYPE_CHECKING:
    from .pitch import Pitch

_MAJOR_INTERVALS: list[tuple[int, int]] = [
    (0, 0),
    (1, 0),
    (2, 0),
    (2, 1),
    (3, 1),
    (4, 1),
    (5, 1),
]

_NAME_RE = re.compile(r"^-?([PpMmAaDd#b]+)?(\d+)$")


class Interval:
    """A distance between two Pitch vectors.

    It can be constructed directly as some number of whole/half steps,
    or via a standard interval name string: Interval.from_name("P5").
    It is also frequently constructed from two Pitch vectors via
    Interval.between(p, q) or p.interval_to(q).
    """

    w: int
    h: int

    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    @classmethod
    def from_name(cls, name: str) -> Interval:
        sign = -1 if name[0] == "-" else 1

        match = _NAME_RE.match(name)
        if not match:
            raise ValueError(f"Invalid interval name: {name}")

        accidental_str = match.group(1) or ""
        generic_size = int(match.group(2))

        simple = (generic_size - 1) % 7
        w, h = _MAJOR_INTERVALS[simple]

        octave = (generic_size - 1) // 7
        w += 5 * octave
        h += 2 * octave

        quality_adjustment = 0
        quality_adjustment += sum(1 for x in accidental_str if x in "Aa#")
        quality_adjustment -= sum(1 for x in accidental_str if x in "mb")
        dims = sum(1 for x in accidental_str if x in "Dd")
        quality_adjustment -= dims
        if dims != 0 and simple not in (0, 3, 4):
            quality_adjustment -= 1

        w += quality_adjustment
        h -= quality_adjustment

        return cls(sign * w, sign * h)

    @classmethod
    def from_spn(cls, ps: str, qs: str) -> Interval:
        """Create an Interval from two pitch names as SPN strings.

        - e.g. Interval.from_spn("C4", "E4")  # produces a major 3rd.
        """
        from .parse.spn import SPN

        return cls.between(SPN.to_pitch(ps), SPN.to_pitch(qs))

    @classmethod
    def between(cls, p: Pitch, q: Pitch) -> Interval:
        """Create an Interval from two passed-in Pitch vectors."""
        return cls(q.w - p.w, q.h - p.h)

    @property
    def chroma(self) -> int:
        """The "chroma" of an Interval is its signed distance from the unison
        in perfect 5ths.
        """
        return self.w * 2 - self.h * 5

    @property
    def is_diatonic(self) -> bool:
        """Returns true if the Interval can occur diatonically."""
        return abs(self.chroma) < 7

    @property
    def is_tonal(self) -> bool:
        """Returns true if the Interval can occur tonally, including via
        chromaticism.
        """
        return abs(self.chroma) < 17

    @property
    def quality(self) -> int:
        """The quality of an Interval as a signed number:

        - 0 is perfect.
        - +1 / -1 are major and minor respectively.
        - +2 / -2 are augmented and diminished respectively.

        etc. for arbitrarily remote Interval qualities.
        """
        sign = -1 if self.stepspan < 0 else 1
        chroma = self.chroma
        if abs(chroma) <= 1:
            return 0
        if 0 < chroma <= 5:
            return sign * math.floor((chroma + 5) / 7)
        if -5 <= chroma < 0:
            return sign * math.ceil((chroma - 5) / 7)
        if chroma > 5:
            return sign * math.floor((chroma + 8) / 7)
        return sign * math.floor((chroma - 2) / 7)

    @property
    def stepspan(self) -> int:
        """The "stepspan" of an Interval: the number of diatonic steps it
        contains, where 0 is the unison, 1 is a generic second and so on.
        """
        return self.w + self.h

    @property
    def pc7(self) -> int:
        """The 0-indexed 7-tone pitch class of an Interval. Essentially its
        size in steps, modulo 7.
        """
        return self.stepspan % 7

    @property
    def pc12(self) -> int:
        """The 12-tone pitch class of an Interval familiar to post-tonal
        theory.
        """
        return (self.w * 2 + self.h) % 12

    @property
    def name(self) -> str:
        """The standard name for an interval."""
        result = ""
        stepspan = self.stepspan
        if stepspan < 0:
            result += "-"
        quality = self.quality
        if quality > 1:
            result += "A" * (quality - 1)
        if quality == 1:
            result += "M"
        if quality == 0:
            result += "P"
        if quality == -1:
            result += "m"
        if quality < -1:
            result += "d" * (-quality - 1)
        result += str(abs(stepspan) + 1)
        return result

    def is_equal(self, m: Interval) -> bool:
        """Returns true if two Interval vectors are identical.

        Note this will NOT return true for intervals that are merely
        enharmonic in 12TET (use is_enharmonic for that).
        """
        return self.w == m.w and self.h == m.h

    def is_enharmonic(self, m: Interval, edo: int = 12) -> bool:
        """Returns true if two Intervals are enharmonic in the specified EDO
        tuning. If no tuning is specified, defaults to 12TET.
        """
        return (self.chroma % edo + edo) % edo == (m.chroma % edo + edo) % edo

    @property
    def negative(self) -> Interval:
        """The flipped version of an interval.

        An ascending major 3rd will become a descending major 3rd.
        Or for vertical intervals, voices will exchange places.
        """
        return Interval(-self.w, -self.h)

    def add(self, m: Interval) -> Interval:
        """Adds an Interval to the current vector.

        Returns a new Interval vector without modifying the original.
        """
        return Interval(self.w + m.w, self.h + m.h)

    def subtract(self, m: Interval) -> Interval:
        """Subtracts an Interval from the current vector.

        Returns a new Interval vector without modifying the original.
        """
        return Interval(self.w - m.w, self.h - m.h)

    def times(self, x: int) -> Interval:
        """Adds an interval to itself the specified number of times."""
        return Interval(self.w * x, self.h * x)

    @property
    def simple(self) -> Interval:
        """The simple (i.e. non-compound / smaller than an octave) version of
        an Interval vector. For simple intervals this will simply be the same
        vector.
        """
        octave = math.trunc((self.w + self.h) / 7)
        return Interval(self.w - octave * 5, self.h - octave * 2)

    class _Range:
        @staticmethod
        def diatonic(
            from_: Optional[Interval] = None, to: Optional[Interval] = None
        ) -> Iterator[Interval]:
            """Generates a range of Intervals between two boundary Intervals
            that can be found within the diatonic scale.
            """
            if from_ is None:
                from_ = Interval(0, 0)
            if to is None:
                to = Interval(5, 2)

            octave = Interval(5, 2)

            current = Interval(from_.w, from_.h)
            middle = current.add(octave)

            offset = -1 if current.quality < 0 else 0
            floor = current.h + offset

            end = to
            while end.subtract(middle).stepspan > 0:
                while current.w <= middle.w:
                    current.h = floor
                    while current.h <= middle.h + 1:
                        if current.is_diatonic:
                            yield Interval(current.w, current.h)
                        current.h += 1
                    current.w += 1
                middle = middle.add(octave)
                floor = current.h + offset
            while current.w <= middle.w:
                current.h = floor
                while current.h <= middle.h + 1:
                    if end.subtract(current).stepspan < 0:
                        current.h += 1
                    if current.w == end.w and current.h > end.h:
                        return
                    if current.is_diatonic:
                        yield Interval(current.w, current.h)
                    current.h += 1
                current.w += 1

        @staticmethod
        def melodic() -> Iterator[Interval]:
            """Generates a range of all the Intervals traditionally
            considered easy for singers to sing. Essentially all the
            diatonic Intervals up to and including the octave, excluding
            A4, d5, m7 and M7.
            """
            m = Interval(0, 0)
            while m.w <= 5:
                while m.h <= 2:
                    if abs(m.chroma) < 6 and m.stepspan != 6:
                        yield Interval(m.w, m.h)
                    m.h += 1
                m.h = 0
                m.w += 1

    range = _Range()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Interval):
            return NotImplemented
        return self.w == other.w and self.h == other.h

    def __add__(self, other: Interval) -> Interval:
        """Operator form of Interval.add: ``m + n``."""
        if not isinstance(other, Interval):
            return NotImplemented
        return Interval(self.w + other.w, self.h + other.h)

    def __sub__(self, other: Interval) -> Interval:
        """Operator form of Interval.subtract: ``m - n``."""
        if not isinstance(other, Interval):
            return NotImplemented
        return Interval(self.w - other.w, self.h - other.h)

    def __neg__(self) -> Interval:
        """Operator form of Interval.negative: ``-m``."""
        return Interval(-self.w, -self.h)

    def __mul__(self, x: int) -> Interval:
        """Operator form of Interval.times: ``m * 3``."""
        if not isinstance(x, int):
            return NotImplemented
        return Interval(self.w * x, self.h * x)

    def __rmul__(self, x: int) -> Interval:
        """Operator form of Interval.times: ``3 * m``."""
        return self.__mul__(x)

    def __repr__(self) -> str:
        return f"Interval(w={self.w!r}, h={self.h!r})"
