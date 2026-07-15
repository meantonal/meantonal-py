import pytest

from meantonal import SPN, Interval, MirrorAxis, Pitch, TonalContext

# Chroma (signed distance from C in perfect 5ths) reference table for the
# note names used below, since SPN parsing doesn't exist until Phase 3:
# naturals: F=-1 C=0 G=1 D=2 A=3 E=4 B=5
# sharps/flats are +/-7 from the natural, double sharps/flats +/-14.


def test_from_chroma_creates_correct_pitch_vector():
    p = Pitch.from_chroma(0, 4)  # C4
    assert (p.w, p.h) == (25, 10)
    p = Pitch.from_chroma(6, 4)  # F#4
    assert (p.w, p.h) == (28, 10)


def test_midi_produces_correct_result():
    assert Pitch.from_chroma(0, -1).midi == 0  # C-1
    assert Pitch.from_chroma(0, 4).midi == 60  # C4
    assert Pitch.from_chroma(3, 4).midi == 69  # A4


def test_midi_raises_outside_standard_range():
    with pytest.raises(ValueError):
        Pitch.from_chroma(0, -2).midi  # below MIDI 0
    with pytest.raises(ValueError):
        Pitch.from_chroma(0, 10).midi  # above MIDI 127


def test_chroma_produces_correct_result():
    assert Pitch.from_chroma(0, 4).chroma == 0  # C4
    assert Pitch.from_chroma(-3, 4).chroma == -3  # Eb4
    assert Pitch.from_chroma(6, 4).chroma == 6  # F#4


def test_pc7_produces_correct_result():
    assert Pitch.from_chroma(1, 4).pc7 == 4  # G4


def test_pc12_produces_correct_result():
    assert Pitch.from_chroma(1, 4).pc12 == 7  # G4


def test_letter_produces_correct_result():
    assert Pitch.from_chroma(0, 4).letter == "C"  # C4
    assert Pitch.from_chroma(6, 4).letter == "F"  # F#4


def test_accidental_produces_correct_result():
    assert Pitch.from_chroma(0, 4).accidental == 0  # C4
    assert Pitch.from_chroma(6, 4).accidental == 1  # F#4
    assert Pitch.from_chroma(11, 4).accidental == 1  # E#4
    assert Pitch.from_chroma(-1, 4).accidental == 0  # F4
    assert Pitch.from_chroma(5, 4).accidental == 0  # B4
    assert Pitch.from_chroma(-2, 4).accidental == -1  # Bb4
    assert Pitch.from_chroma(-8, 4).accidental == -1  # Fb4
    assert Pitch.from_chroma(13, 4).accidental == 2  # Fx4


def test_octave_produces_correct_result():
    assert Pitch.from_chroma(0, 4).octave == 4  # C4
    assert Pitch.from_chroma(5, 4).octave == 4  # B4
    assert Pitch.from_chroma(0, 3).octave == 3  # C3
    assert Pitch.from_chroma(5, 3).octave == 3  # B3
    assert Pitch.from_chroma(0, -1).octave == -1  # C-1
    assert Pitch.from_chroma(5, -1).octave == -1  # B-1


def test_steps_to_produces_correct_result():
    p = Pitch.from_chroma(0, 4)  # C4
    q = Pitch.from_chroma(6, 4)  # F#4
    assert p.steps_to(q) == 3
    q = Pitch.from_chroma(-4, 3)  # Ab3
    assert p.steps_to(q) == -2
    q = Pitch.from_chroma(7, 4)  # C#4
    assert p.steps_to(q) == 0


def test_is_equal_produces_correct_result():
    p = Pitch.from_chroma(7, 4)  # C#4
    q = Pitch.from_chroma(7, 5)  # C#5
    assert not p.is_equal(q)
    q = Pitch.from_chroma(-5, 3)  # Db3
    assert not p.is_equal(q)
    q = Pitch.from_chroma(7, 4)  # C#4
    assert p.is_equal(q)


def test_is_enharmonic_produces_correct_result():
    p = Pitch.from_chroma(7, 4)  # C#4
    q = Pitch.from_chroma(7, 5)  # C#5
    assert p.is_enharmonic(q)
    q = Pitch.from_chroma(-5, 5)  # Db5
    assert p.is_enharmonic(q)
    assert not p.is_enharmonic(q, 31)

    p = Pitch.from_chroma(18, 4)  # Ex4 (E double sharp)
    q = Pitch.from_chroma(-13, 5)  # Gbb5
    assert p.is_enharmonic(q, 31)
    assert not p.is_enharmonic(q)


def test_transpose_real_produces_correct_result():
    p = Pitch.from_chroma(0, 4)  # C4
    q = Pitch.from_chroma(6, 4)  # F#4
    m = Interval.from_name("A4")
    assert p.transpose_real(m).is_equal(q)


def test_invert_produces_correct_result():
    axis = MirrorAxis(Pitch.from_chroma(0, 4), Pitch.from_chroma(1, 4))  # C4, G4
    p = Pitch.from_chroma(4, 4)  # E4
    q = Pitch.from_chroma(-3, 4)  # Eb4
    assert p.invert(axis).is_equal(q)
    p = Pitch.from_chroma(2, 4)  # D4
    q = Pitch.from_chroma(-1, 4)  # F4
    assert p.invert(axis).is_equal(q)


# --- Operator overloading (affine pitch/interval arithmetic) ---------------


def test_operator_pitch_plus_interval_matches_transpose_real():
    p = Pitch.from_chroma(0, 4)  # C4
    q = Pitch.from_chroma(6, 4)  # F#4
    m = Interval.from_name("A4")
    assert p + m == q
    assert m + p == q  # commutes, like timedelta + datetime
    assert p + m == p.transpose_real(m)


def test_operator_pitch_minus_interval_transposes_down():
    p = Pitch.from_chroma(6, 4)  # F#4
    m = Interval.from_name("A4")
    q = Pitch.from_chroma(0, 4)  # C4
    assert p - m == q
    assert p - m == p.transpose_real(m.negative)


def test_operator_pitch_minus_pitch_gives_interval_between():
    p = Pitch.from_chroma(0, 4)  # C4
    q = Pitch.from_chroma(4, 4)  # E4
    assert q - p == Interval.from_name("M3")
    assert q - p == Interval.between(p, q)
    assert p - q == Interval.from_name("M3").negative


def test_operator_pitch_plus_pitch_is_undefined():
    p = Pitch.from_chroma(0, 4)
    q = Pitch.from_chroma(4, 4)
    with pytest.raises(TypeError):
        p + q


# --- Tests requiring TonalContext (deferred from Phase 2, back-filled here) --


def test_from_degree_creates_correct_pitch_vector():
    context = TonalContext.from_strings("C", "major")
    p = Pitch.from_degree(0, 0, 4, context)
    assert (p.w, p.h) == (25, 10)
    p = Pitch.from_degree(0, 2, 4, context)
    assert (p.w, p.h) == (27, 8)
    p = Pitch.from_degree(5, -1, 3, context)
    assert (p.w, p.h) == (23, 10)


def test_range_diatonic_produces_correct_range():
    from_ = SPN.to_pitch("C4")
    to = SPN.to_pitch("C5")
    context = TonalContext.from_strings("C", "major")
    names = [SPN.from_pitch(p) for p in Pitch.range.diatonic(from_, to, context)]
    for expected in ("C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"):
        assert expected in names
    for unexpected in ("C#4", "B3", "C#5", "Db5"):
        assert unexpected not in names


def test_range_chromatic_produces_correct_range():
    from_ = SPN.to_pitch("C4")
    to = SPN.to_pitch("E5")
    context = TonalContext.from_strings("C", "major")
    names = [SPN.from_pitch(p) for p in Pitch.range.chromatic(from_, to, context)]
    for expected in (
        "C4",
        "C#4",
        "Db4",
        "D4",
        "D#4",
        "Eb4",
        "E4",
        "F4",
        "F#4",
        "Gb4",
        "G4",
        "G#4",
        "Ab4",
        "A4",
        "A#4",
        "Bb4",
        "B4",
        "C5",
        "C#5",
        "Db5",
        "D5",
        "D#5",
        "Eb5",
        "E5",
    ):
        assert expected in names
    for unexpected in ("B3", "E#4", "Fb4", "F5"):
        assert unexpected not in names
