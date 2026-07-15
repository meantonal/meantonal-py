from __future__ import annotations

import math
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .interval import Interval
    from .pitch import Pitch

_FIFTH_MIN = 1200 * 4 / 7
_FIFTH_MAX = 1200 * 3 / 5


class MapVec:
    """An indeterminate vector type to be used with the Map1D and Map2D classes.

    Can be converted to Pitch or Interval vectors as needed using its methods.
    """

    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def to_pitch(self) -> Pitch:
        """Converts a MapVec into a Pitch vector.

        Returns a new vector. Does not modify the MapVec.
        """
        from .pitch import Pitch

        return Pitch(self.x, self.y)

    def to_interval(self) -> Interval:
        """Converts a MapVec into an Interval vector.

        Returns a new vector. Does not modify the MapVec.
        """
        from .interval import Interval

        return Interval(self.x, self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MapVec):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        return f"MapVec(x={self.x!r}, y={self.y!r})"


class Map1D:
    """Represents a 1x2 matrix. Used to effect an arbitrary linear map from
    2d vectors down to 1d numbers.
    """

    m0: float
    m1: float

    def __init__(self, m0: float, m1: float) -> None:
        self.m0 = m0
        self.m1 = m1

    def map(self, v: Union[MapVec, Pitch, Interval]) -> float:
        """Multiplies the matrix with the passed in vector.

        Returns a number.
        """
        if isinstance(v, MapVec):
            return self.m0 * v.x + self.m1 * v.y
        return self.m0 * v.w + self.m1 * v.h

    def compose(self, map: Map2D) -> Map1D:
        return Map1D(
            self.m0 * map.m00 + self.m1 * map.m10,
            self.m0 * map.m01 + self.m1 * map.m11,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Map1D):
            return NotImplemented
        return self.m0 == other.m0 and self.m1 == other.m1

    def __repr__(self) -> str:
        return f"Map1D(m0={self.m0!r}, m1={self.m1!r})"


class Map2D:
    """Represents a 2x2 matrix. Used to effect an arbitrary basis change from one
    coordinates system to another.
    """

    m00: float
    m01: float
    m10: float
    m11: float

    def __init__(self, m00: float, m01: float, m10: float, m11: float) -> None:
        self.m00 = m00
        self.m01 = m01
        self.m10 = m10
        self.m11 = m11

    def map(self, v: Union[MapVec, Pitch, Interval]) -> MapVec:
        """Multiplies the matrix with the passed in vector.

        Returns a MapVec.
        """
        if isinstance(v, MapVec):
            return MapVec(
                self.m00 * v.x + self.m01 * v.y,
                self.m10 * v.x + self.m11 * v.y,
            )
        return MapVec(
            self.m00 * v.w + self.m01 * v.h,
            self.m10 * v.w + self.m11 * v.h,
        )

    def compose(self, map: Map2D) -> Map2D:
        return Map2D(
            self.m00 * map.m00 + self.m01 * map.m10,
            self.m00 * map.m01 + self.m01 * map.m11,
            self.m10 * map.m00 + self.m11 * map.m10,
            self.m10 * map.m01 + self.m11 * map.m11,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Map2D):
            return NotImplemented
        return (
            self.m00 == other.m00
            and self.m01 == other.m01
            and self.m10 == other.m10
            and self.m11 == other.m11
        )

    def __repr__(self) -> str:
        return (
            f"Map2D(m00={self.m00!r}, m01={self.m01!r}, "
            f"m10={self.m10!r}, m11={self.m11!r})"
        )


class TuningMap:
    """Represents a map onto a given tuning system. Specified in terms of
    the width of its fifth in cents, and the name and frequency of a
    reference pitch in Hz (e.g. A = 440).

    - Reference pitch is optional, defaults to C4 = 261.6255653Hz.
    """

    def __init__(
        self,
        fifth: float,
        reference_pitch: str = "C4",
        reference_freq: float = 261.6255653,
    ) -> None:
        if fifth < _FIFTH_MIN or fifth > _FIFTH_MAX:
            raise ValueError(
                "TuningMap requires a fifth between ~685.7¢ and 720¢ to "
                "produce a well-defined diatonic."
            )
        from .parse.spn import SPN

        self._reference_pitch: Pitch = SPN.to_pitch(reference_pitch)
        self._reference_freq = reference_freq
        self._cent_map = Map1D(fifth, 1200)

    @classmethod
    def from_edo(
        cls,
        edo: int,
        reference_pitch: str = "C4",
        reference_freq: float = 261.6255653,
    ) -> TuningMap:
        """Initialises an EDO tuning map by specifying the number of parts
        to divide the octave into rather than the width of the fifth in
        cents.
        """
        fifth_steps = round(math.log2(1.5) * edo)
        fifth = (fifth_steps * 1200) / edo

        if fifth < _FIFTH_MIN or fifth > _FIFTH_MAX:
            raise ValueError(f"{edo}-EDO does not support a diatonic scale.")

        return cls(fifth, reference_pitch, reference_freq)

    def to_cents(self, m: Interval) -> float:
        """Renders the width of an Interval in cents."""
        from .constants import GENERATORS_TO

        return self._cent_map.map(GENERATORS_TO.map(m))

    def to_ratio(self, m: Interval) -> float:
        """Renders the ratio of an Interval vector as a decimal number."""
        return 2 ** (self.to_cents(m) / 1200)

    def to_hz(self, p: Pitch) -> float:
        """Renders the frequency of a Pitch vector in Hertz."""
        return self._reference_freq * self.to_ratio(
            self._reference_pitch.interval_to(p)
        )


class EDOMap:
    """Transforms Pitch vectors into an ordered integer representation for a
    given EDO tuning. In 12TET, this numbering exactly corresponds to
    standard MIDI, and is designed to provide an analogous numbering for
    other EDO tunings.
    """

    def __init__(self, edo: int) -> None:
        fifth_steps = round(math.log2(1.5) * edo)

        fifth = (fifth_steps * 1200) / edo
        if fifth < _FIFTH_MIN or fifth > _FIFTH_MAX:
            raise ValueError(f"{edo}-EDO does not support a diatonic scale.")

        whole = (fifth_steps * 2 % edo + edo) % edo
        half = (fifth_steps * -5 % edo + edo) % edo
        self._map = Map1D(whole, half)

    def to_number(self, p: Pitch) -> float:
        """Renders the ordered pitch number of a Pitch vector.

        In 12TET, this will be the MIDI value of a Pitch, and provides an
        analogous ordered numbering for other EDO tuning systems.
        """
        return self._map.map(p)

    def compare(self, p: Pitch, q: Pitch) -> float:
        """Returns a positive value if p sounds above q.

        Returns a negative value if p sounds below q.
        Returns 0 if p and q are enharmonic.
        """
        return self._map.map(p) - self._map.map(q)
