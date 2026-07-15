## Table of Contents

- [Meantonal](#meantonal)
- [Installation](#installation)
- [Documentation](#documentation)

<img align="left" src="/logo.svg" width="48">
  
# Meantonal

Meantonal is a specification for representing pitch information in Western music, and a suite of tools for operating on this information. It's a small, focused library that aims to empower developers to build musical apps more easily.

Meantonal is:

- **Flexible with I/O**: easily ingest and translate between Scientific Pitch Notation, Helmholtz notation, ABC and Lilypond. Extract MIDI values at any time.
- **Semantically nondestructive**: the distinction between enharmonic notes such as C♯ and D♭ is maintained. Things that don't behave the same way musically are not encoded the same way in Meantonal.
- **Just vectors**: under the hood [pitches](https://meantonal.org/learn/pitch/) and [intervals](https://meantonal.org/learn/intervals/) are 2d vectors. Operations are simple to understand, surprisingly powerful, and fast to execute.
- **Tuning-agnostic**: Target any meantone tuning system, not just 12-tone equal temperament. You want 31 tones per octave? Done.

For the JS/TS implementation of Meantonal [click here](https://github.com/meantonal/meantonal-js), or for the C implementation [click here](https://github.com/meantonal/meantonal-c).

## Installation

Adding Meantonal to your project is as simple as running:

```bash
pip install meantonal
```

You're now ready to import and use Meantonal's classes.

```python
from meantonal import SPN, Helmholtz, Interval, TonalContext, MirrorAxis

p = SPN.to_pitch("C4")
q = Helmholtz.to_pitch("e'")

m = p.interval_to(q)  # M3
n = Interval.from_name("M3")

m.is_equal(n)  # True

context = TonalContext.from_strings("Eb", "major")

q = q.snap_to(context)  # q has now snapped to Eb4

axis = MirrorAxis.from_spn("D4", "A4")

q = q.invert(axis)  # q is now G#4
```

Since pitches and intervals are just vectors, the Python implementation also
supports natural arithmetic on them, in the style of `datetime`/`timedelta`:

```python
from meantonal import SPN, Interval

p = SPN.to_pitch("C4")
m = Interval.from_name("M3")

q = p + m       # E4 -- same as p.transpose_real(m)
q - p           # M3 -- same as Interval.between(p, q)
p - m           # Ab3 -- transpose down
m + m           # A5 (augmented 5th) -- same as m.add(m)
-m              # descending M3 -- same as m.negative
m * 3           # A7 -- same as m.times(3)
```

## Documentation

A full reference of the Python implementation of Meantonal can be found [here](https://meantonal.org/python)
