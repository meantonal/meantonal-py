import pytest

from meantonal import ABC, Helmholtz, Interval, LilyPond, SPN


# --- SPN -------------------------------------------------------------


def test_spn_to_pitch_creates_correct_pitch_vector():
    p = SPN.to_pitch("C4")
    assert (p.w, p.h) == (25, 10)
    p = SPN.to_pitch("C-1")
    assert (p.w, p.h) == (0, 0)
    p = SPN.to_pitch("F##4")
    assert (p.w, p.h) == (29, 9)
    p = SPN.to_pitch("Fx4")
    assert (p.w, p.h) == (29, 9)
    p = SPN.to_pitch("Eb4")
    assert (p.w, p.h) == (26, 11)
    p = SPN.to_pitch("Ew4")
    assert (p.w, p.h) == (25, 12)


def test_spn_to_pitch_raises_for_invalid_string():
    with pytest.raises(ValueError):
        SPN.to_pitch("H4")


def test_spn_from_pitch_produces_correct_result():
    p = SPN.to_pitch("C4")
    assert SPN.from_pitch(p) == "C4"
    p = SPN.to_pitch("Cx-1")
    assert SPN.from_pitch(p) == "Cx-1"
    p = SPN.to_pitch("Gbbbb7")
    assert SPN.from_pitch(p) == "Gbbbb7"


def test_spn_from_pitch_raises_for_accidental_beyond_8():
    # Adding n to w and subtracting n from h raises the accidental by n
    # without changing the letter or octave.
    p = SPN.to_pitch("C4")
    p.w += 8
    p.h -= 8
    assert SPN.from_pitch(p) == "C" + "#" * 8 + "4"
    p.w += 1
    p.h -= 1
    with pytest.raises(ValueError):
        SPN.from_pitch(p)


# --- LilyPond ----------------------------------------------------------


def test_lily_to_pitch_creates_correct_pitch_vector():
    p = LilyPond.to_pitch("c'")
    assert (p.w, p.h) == (25, 10)
    p = LilyPond.to_pitch("c,,,,")
    assert (p.w, p.h) == (0, 0)
    p = LilyPond.to_pitch("fisis'")
    assert (p.w, p.h) == (29, 9)
    p = LilyPond.to_pitch("ees'")
    assert (p.w, p.h) == (26, 11)
    p = LilyPond.to_pitch("eeses'")
    assert (p.w, p.h) == (25, 12)


def test_lily_to_pitch_raises_for_invalid_string():
    with pytest.raises(ValueError):
        LilyPond.to_pitch("h")


def test_lily_from_pitch_round_trips():
    for lily in ("c'", "aes", "gisis'''", "eeses,,,,"):
        p = LilyPond.to_pitch(lily)
        assert LilyPond.from_pitch(p) == lily


def test_lily_from_pitch_raises_for_accidental_beyond_2():
    p = LilyPond.to_pitch("c")
    p.w += 2
    p.h -= 2
    assert LilyPond.from_pitch(p) == "c" + "is" * 2
    p.w += 1
    p.h -= 1
    with pytest.raises(ValueError):
        LilyPond.from_pitch(p)

    p = LilyPond.to_pitch("c")
    p.w -= 2
    p.h += 2
    assert LilyPond.from_pitch(p) == "c" + "es" * 2
    p.w -= 1
    p.h += 1
    with pytest.raises(ValueError):
        LilyPond.from_pitch(p)


def test_lily_from_pitch_raises_for_octave_outside_range():
    # Adding (5, 2) transposes up an octave without changing the accidental.
    p = LilyPond.to_pitch("c")
    assert p.octave == 3
    p.w += 5 * 8
    p.h += 2 * 8
    assert p.octave == 11
    assert LilyPond.from_pitch(p) == "c" + "'" * 8
    p.w += 5
    p.h += 2
    with pytest.raises(ValueError):
        LilyPond.from_pitch(p)

    p = LilyPond.to_pitch("c")
    p.w -= 5 * 6
    p.h -= 2 * 6
    assert p.octave == -3
    assert LilyPond.from_pitch(p) == "c" + "," * 6
    p.w -= 5
    p.h -= 2
    with pytest.raises(ValueError):
        LilyPond.from_pitch(p)


def test_lily_relative_parser_creates_correct_pitch_vector():
    p = SPN.to_pitch("C4")
    parser = LilyPond.relative(p)
    p = parser.to_pitch("g")
    assert (p.w, p.h) == (23, 9)
    p = parser.to_pitch("fisis'")
    assert (p.w, p.h) == (29, 9)
    p = parser.to_pitch("c")
    assert (p.w, p.h) == (25, 10)


# --- Helmholtz -----------------------------------------------------------


def test_helmholtz_to_pitch_produces_correct_result():
    p = Helmholtz.to_pitch("c'")
    assert (p.w, p.h) == (25, 10)
    p = Helmholtz.to_pitch("c")
    assert (p.w, p.h) == (20, 8)
    p = Helmholtz.to_pitch("C")
    assert (p.w, p.h) == (15, 6)
    p = Helmholtz.to_pitch("C,")
    assert (p.w, p.h) == (10, 4)
    p = Helmholtz.to_pitch("f#''")
    assert (p.w, p.h) == (33, 12)


def test_helmholtz_to_pitch_raises_for_invalid_string():
    with pytest.raises(ValueError):
        Helmholtz.to_pitch("h")


def test_helmholtz_from_pitch_round_trips():
    for helm in ("c", "C#", "Cb,,", "fx'''"):
        p = Helmholtz.to_pitch(helm)
        assert Helmholtz.from_pitch(p) == helm


def test_helmholtz_from_pitch_raises_for_accidental_beyond_8():
    p = Helmholtz.to_pitch("c")
    p.w += 8
    p.h -= 8
    assert Helmholtz.from_pitch(p) == "c" + "#" * 8
    p.w += 1
    p.h -= 1
    with pytest.raises(ValueError):
        Helmholtz.from_pitch(p)


def test_helmholtz_from_pitch_raises_for_octave_outside_range():
    p = Helmholtz.to_pitch("c'")  # octave 4
    assert p.octave == 4
    p.w += 5 * 7
    p.h += 2 * 7
    assert p.octave == 11
    assert Helmholtz.from_pitch(p) == "c" + "'" * 8
    p.w += 5
    p.h += 2
    with pytest.raises(ValueError):
        Helmholtz.from_pitch(p)

    p = Helmholtz.to_pitch("C")  # octave 2
    assert p.octave == 2
    p.w -= 5 * 5
    p.h -= 2 * 5
    assert p.octave == -3
    assert Helmholtz.from_pitch(p) == "C" + "," * 5
    p.w -= 5
    p.h -= 2
    with pytest.raises(ValueError):
        Helmholtz.from_pitch(p)


# --- ABC -------------------------------------------------------------


def test_abc_to_pitch_produces_correct_result():
    p = ABC.to_pitch("C")
    assert (p.w, p.h) == (25, 10)
    p = ABC.to_pitch("c")
    assert (p.w, p.h) == (30, 12)
    p = ABC.to_pitch("c'")
    assert (p.w, p.h) == (35, 14)
    p = ABC.to_pitch("C,")
    assert (p.w, p.h) == (20, 8)
    p = ABC.to_pitch("^f")
    assert (p.w, p.h) == (33, 12)


def test_abc_to_pitch_raises_for_invalid_string():
    with pytest.raises(ValueError):
        ABC.to_pitch("h")


def test_abc_from_pitch_round_trips():
    for abc in ("c", "^C", "_C,,", "^^f'''"):
        p = ABC.to_pitch(abc)
        assert ABC.from_pitch(p) == abc


def test_abc_from_pitch_raises_for_accidental_beyond_2():
    p = ABC.to_pitch("c")
    p.w += 2
    p.h -= 2
    assert ABC.from_pitch(p) == "^" * 2 + "c"
    p.w += 1
    p.h -= 1
    with pytest.raises(ValueError):
        ABC.from_pitch(p)

    p = ABC.to_pitch("c")
    p.w -= 2
    p.h += 2
    assert ABC.from_pitch(p) == "_" * 2 + "c"
    p.w -= 1
    p.h += 1
    with pytest.raises(ValueError):
        ABC.from_pitch(p)


def test_abc_from_pitch_raises_for_octave_outside_range():
    p = ABC.to_pitch("c")
    assert p.octave == 5
    p.w += 5 * 6
    p.h += 2 * 6
    assert p.octave == 11
    assert ABC.from_pitch(p) == "c" + "'" * 6
    p.w += 5
    p.h += 2
    with pytest.raises(ValueError):
        ABC.from_pitch(p)

    p = ABC.to_pitch("c")
    p.w -= 5 * 8
    p.h -= 2 * 8
    assert p.octave == -3
    assert ABC.from_pitch(p) == "C" + "," * 7
    p.w -= 5
    p.h -= 2
    with pytest.raises(ValueError):
        ABC.from_pitch(p)


# --- Interval.from_spn / MirrorAxis.from_spn (deferred from Phase 2) -----


def test_interval_from_spn_creates_correct_interval_vector():
    m = Interval.from_name("M3")
    n = Interval.from_spn("C4", "E4")
    assert m.is_equal(n)


def test_mirror_axis_from_spn_creates_correct_axis():
    from meantonal import MirrorAxis

    axis = MirrorAxis.from_spn("C4", "G4")
    p = SPN.to_pitch("E4")
    q = SPN.to_pitch("Eb4")
    assert p.invert(axis).is_equal(q)
