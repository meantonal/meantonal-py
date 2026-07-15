from __future__ import annotations

import functools
import math
from typing import TYPE_CHECKING, Iterator, Optional

from .interval import Interval

if TYPE_CHECKING:
    from .map import TuningMap
    from .tonality import TonalContext


class Pitch:
    """The most fundamental type in Meantonal.

    - Can be constructed from some number of whole steps and half steps from
      C-1 (the lowest MIDI note).
    - Can also be constructed using static methods like Pitch.from_chroma().
    """

    w: int
    h: int

    def __init__(self, w: int, h: int) -> None:
        self.w = w
        self.h = h

    @classmethod
    def from_chroma(cls, chroma: int, octave: int) -> Pitch:
        """Create a Pitch vector from a chroma value (the signed distance of
        a note name from "C" in perfect fifths), and an octave number (in
        SPN numbering).
        """
        w, h = chroma * 3, chroma
        octave += 1
        while (w + h) / 7 > octave:
            w -= 5
            h -= 2
        while (w + h) / 7 < octave:
            w += 5
            h += 2
        return cls(w, h)

    @classmethod
    def from_degree(
        cls, degree: int, alteration: int, octave: int, context: TonalContext
    ) -> Pitch:
        """Returns a Pitch specified by its degree (0-indexed so the tonic is
        0) and alteration (0 == diatonic) within a TonalContext, along with
        its octave number (SPN numbering).

        Note: this function doesn't enforce the 17-fifths window used to
        define keys, and will happily produce a degree altered by 4
        chromatic semitones.
        """
        return cls.from_chroma(context.degree_chroma(degree, alteration), octave)

    @property
    def midi(self) -> int:
        """Returns the standard MIDI number for a Pitch.

        Raises ValueError if outside of the standard MIDI range 0 <= x < 128.
        """
        midi = 2 * self.w + self.h
        if 0 <= midi < 128:
            return midi
        raise ValueError(f"Outside of standard MIDI range: {midi}")

    @property
    def chroma(self) -> int:
        """The signed distance of a Pitch from "C" in perfect 5ths."""
        return self.w * 2 - self.h * 5

    @property
    def pc7(self) -> int:
        """The 0-indexed 7-tone pitch class of a Pitch. Equivalent to a
        numerical representation of its letter name. C is 0.
        """
        return (self.w + self.h) % 7

    @property
    def pc12(self) -> int:
        """The 12-tone pitch class of a Pitch. C is 0."""
        return self.midi % 12

    @property
    def letter(self) -> str:
        """The letter component of a Pitch as a string, e.g. Db4 -> "D"."""
        return "CDEFGAB"[self.pc7]

    @property
    def accidental(self) -> int:
        """The accidental component of a Pitch as a number:

        - Natural notes return 0.
        - Sharp notes return 1.
        - Flat notes return -1.
        - Double sharps and double flats return 2 and -2.

        etc. for arbitrary accidentals.
        """
        return math.floor((self.chroma + 1) / 7)

    @property
    def octave(self) -> int:
        """The octave number of a Pitch (in SPN numbering)."""
        return math.floor((self.w + self.h) / 7 - 1)

    def steps_to(self, p: Pitch) -> int:
        """Returns the signed number of diatonic steps to reach the passed-in
        Pitch.
        """
        return (p.w + p.h) - (self.w + self.h)

    def is_equal(self, p: Pitch) -> bool:
        """Returns true if two Pitch vectors are identical.

        Note this will NOT return true for notes that are merely enharmonic
        in 12TET (use is_enharmonic for that).
        """
        return self.w == p.w and self.h == p.h

    def is_enharmonic(self, p: Pitch, edo: int = 12) -> bool:
        """Returns true if two notes are enharmonic in the specified EDO
        tuning. If no tuning is specified, defaults to 12TET.
        """
        return (self.chroma % edo + edo) % edo == (p.chroma % edo + edo) % edo

    def interval_to(self, p: Pitch) -> Interval:
        """Returns the interval from the current Pitch to another passed-in
        vector.
        """
        return Interval.between(self, p)

    def transpose_real(self, m: Interval) -> Pitch:
        """Transpose a Pitch vector by the passed in Interval vector.

        Returns the transposed Pitch as a new vector. Does not modify the
        original Pitch.
        """
        return Pitch(self.w + m.w, self.h + m.h)

    def invert(self, axis: MirrorAxis) -> Pitch:
        """Invert a Pitch vector about the passed in axis.

        A MirrorAxis is created from two Pitches, either directly or via
        MirrorAxis.from_spn() using two SPN strings.
        Returns the inverted Pitch as a new vector. Does not modify the
        original Pitch.
        """
        return Pitch(axis.w - self.w, axis.h - self.h)

    def degree_in(self, context: TonalContext) -> int:
        """Returns the scale degree number represented by a Pitch in the
        passed-in TonalContext.

        Note that this number is 0-indexed. 0 is the tonic of a key or mode.
        """
        return context.degree_number(self)

    def alteration_in(self, context: TonalContext) -> int:
        """Returns the scale degree alteration represented by a Pitch in the
        passed-in TonalContext, e.g. C# is a raised note in the key of C
        major.

        0 represents a diatonic Pitch in the TonalContext.
        +1 / -1 represent a raised or lowered Pitch in the TonalContext.
        +2 / -2 represent Pitches too remote to belong in a given
        TonalContext.
        """
        return context.degree_alteration(self)

    def snap_to(self, context: TonalContext) -> Pitch:
        """Snaps a Pitch vector to the diatonic position for that
        letter-name in the passed-in TonalContext.
        """
        return context.snap_diatonic(self)

    def transpose_diatonic(self, steps: int, context: TonalContext) -> Pitch:
        """Transpose a Pitch vector by a generic interval specified as a
        simple number, snapping to diatonic values.

        - Measured in steps, such that 0 is a unison.
        """
        return self.transpose_real(Interval(steps, 0)).snap_to(context)

    class _Range:
        @staticmethod
        def diatonic(
            from_: Pitch, to: Pitch, context: TonalContext
        ) -> Iterator[Pitch]:
            """Create a diatonic range of Pitch vectors between two specified
            pitches in a given TonalContext.
            """
            m = Pitch(from_.w, from_.h)
            yield m.snap_to(context)
            while m.steps_to(to) > 0:
                m = m.transpose_diatonic(1, context)
                yield Pitch(m.w, m.h)

        @staticmethod
        def chromatic(
            from_: Pitch, to: Pitch, context: TonalContext
        ) -> Iterator[Pitch]:
            """Create a full chromatic range of Pitch vectors between two
            specified pitches in a given TonalContext.

            Only pitches which could represent either diatonic or altered
            degrees in the passed-in context will be included.
            """
            if from_.interval_to(to).stepspan < 0:
                from_, to = to, from_

            # If the lower boundary is outside the chromatic space of the
            # key, adjust as needed.
            current = Pitch(from_.w, from_.h)
            while current.alteration_in(context) < -1:
                current.w += 1
                current.h -= 1
            if current.alteration_in(context) > 1:
                while current.alteration_in(context) > 1:
                    current.w -= 1
                    current.h += 1
                current.h += 1

            # If the upper boundary is outside the chromatic space of the
            # key, adjust as needed.
            end = Pitch(to.w, to.h)
            while end.alteration_in(context) > 1:
                end.w -= 1
                end.h += 1
            if end.alteration_in(context) < -1:
                while end.alteration_in(context) < -1:
                    end.w += 1
                    end.h -= 1
                end.h -= 1

            yield Pitch(current.w, current.h)
            while not current.is_equal(end):
                if current.alteration_in(context) == -1:
                    current.w += 1
                    current.h -= 2
                else:
                    current.h += 1
                yield Pitch(current.w, current.h)

    range = _Range()

    @staticmethod
    def audible(p: Pitch, T: Optional[TuningMap] = None) -> bool:
        """Returns true if p is within the approximate average range of
        human hearing. That is, roughly: between 20Hz - 20kHz.
        """
        if T is None:
            from .map import TuningMap

            T = TuningMap.from_edo(12)
        f = T.to_hz(p)
        if f < 20:
            return False
        if f > 20000:
            return False
        return True

    @staticmethod
    def highest(arr: list[Pitch], T: Optional[TuningMap] = None) -> Pitch:
        """Returns the highest Pitch in a passed-in list of Pitches.

        Uses optional passed-in TuningMap to decide whether one Pitch is
        higher than another, defaults to 12TET.
        """
        if T is None:
            from .map import TuningMap

            T = TuningMap.from_edo(12)
        tuning = T

        def reducer(a: Pitch, c: Pitch) -> Pitch:
            if tuning.to_hz(a) > tuning.to_hz(c):
                return a
            if tuning.to_hz(a) < tuning.to_hz(c):
                return c
            if a.steps_to(c) < 0:
                return a
            return c

        return functools.reduce(reducer, arr)

    @staticmethod
    def lowest(arr: list[Pitch], T: Optional[TuningMap] = None) -> Pitch:
        """Returns the lowest Pitch in a passed-in list of Pitches.

        Uses optional passed-in TuningMap to decide whether one Pitch is
        lower than another, defaults to 12TET.
        """
        if T is None:
            from .map import TuningMap

            T = TuningMap.from_edo(12)
        tuning = T

        def reducer(a: Pitch, c: Pitch) -> Pitch:
            if tuning.to_hz(a) < tuning.to_hz(c):
                return a
            if tuning.to_hz(a) > tuning.to_hz(c):
                return c
            if a.steps_to(c) > 0:
                return a
            return c

        return functools.reduce(reducer, arr)

    def nearest(self, arr: list[Pitch], T: Optional[TuningMap] = None) -> Pitch:
        """Returns the Pitch in a list of Pitches closest to the calling
        Pitch.

        Uses optional passed-in TuningMap to decide whether one Pitch is
        closer than another, defaults to 12TET.
        """
        if T is None:
            from .map import TuningMap

            T = TuningMap.from_edo(12)
        tuning = T

        def oriented_ratio_between(p: Pitch, q: Pitch) -> float:
            return max(
                tuning.to_ratio(p.interval_to(q)), tuning.to_ratio(q.interval_to(p))
            )

        nearest_by_ratio = sorted(arr, key=lambda p: oriented_ratio_between(self, p))[
            0
        ]

        filtered_by_hz = [
            p
            for p in arr
            if oriented_ratio_between(self, p)
            == oriented_ratio_between(self, nearest_by_ratio)
        ]

        return sorted(filtered_by_hz, key=lambda p: self.steps_to(p))[0]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return self.w == other.w and self.h == other.h

    def __add__(self, other: Interval) -> Pitch:
        """Operator form of Pitch.transpose_real: ``p + m``.

        A Pitch is a point and an Interval is a displacement, so
        Pitch + Interval gives a new Pitch (like datetime + timedelta).
        Pitch + Pitch is deliberately not defined.
        """
        if not isinstance(other, Interval):
            return NotImplemented
        return Pitch(self.w + other.w, self.h + other.h)

    __radd__ = __add__

    def __sub__(self, other: Pitch | Interval) -> Pitch | Interval:
        """Subtraction in the pitch/interval affine space.

        - ``p - m`` (Pitch - Interval) transposes down, returning a Pitch.
        - ``q - p`` (Pitch - Pitch) returns the Interval from p to q,
          i.e. Interval.between(p, q) (like datetime - datetime).
        """
        if isinstance(other, Interval):
            return Pitch(self.w - other.w, self.h - other.h)
        if isinstance(other, Pitch):
            return Interval(self.w - other.w, self.h - other.h)
        return NotImplemented

    def __repr__(self) -> str:
        return f"Pitch(w={self.w!r}, h={self.h!r})"


class MirrorAxis:
    """Used to invert pitches about a fixed point.

    It can be defined by two Pitch vectors that will invert to each other.
    """

    w: int
    h: int

    def __init__(self, p: Pitch, q: Pitch) -> None:
        self.w = p.w + q.w
        self.h = p.h + q.h

    @classmethod
    def from_spn(cls, ps: str, qs: str) -> MirrorAxis:
        from .parse.spn import SPN

        return cls(SPN.to_pitch(ps), SPN.to_pitch(qs))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MirrorAxis):
            return NotImplemented
        return self.w == other.w and self.h == other.h

    def __repr__(self) -> str:
        return f"MirrorAxis(w={self.w!r}, h={self.h!r})"
