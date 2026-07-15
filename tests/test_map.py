import pytest

from meantonal import SPN, EDOMap, Interval, Map1D, Map2D, MapVec, Pitch, TuningMap


class _VecLike:
    """Minimal stand-in for Pitch/Interval (duck-typed via .w/.h) for testing
    Map1D/Map2D without depending on those classes.
    """

    def __init__(self, w: float, h: float) -> None:
        self.w = w
        self.h = h


def test_mapvec_construction_and_equality():
    v = MapVec(3, 4)
    assert v.x == 3
    assert v.y == 4
    assert v == MapVec(3, 4)
    assert v != MapVec(3, 5)
    assert v != "not a mapvec"


def test_mapvec_repr():
    assert repr(MapVec(1, 2)) == "MapVec(x=1, y=2)"


def test_map1d_maps_mapvec():
    m = Map1D(2, 3)
    assert m.map(MapVec(5, 7)) == 2 * 5 + 3 * 7


def test_map1d_maps_duck_typed_vector():
    m = Map1D(2, 3)
    assert m.map(_VecLike(5, 7)) == 2 * 5 + 3 * 7


def test_map1d_compose():
    m = Map1D(1, 2)
    n = Map2D(3, 4, 5, 6)
    composed = m.compose(n)
    assert isinstance(composed, Map1D)
    assert composed.m0 == 1 * 3 + 2 * 5
    assert composed.m1 == 1 * 4 + 2 * 6
    # composed.map(v) should equal m.map(n.map(v)) for any vector v.
    v = MapVec(7, 9)
    assert composed.map(v) == m.map(n.map(v))


def test_map2d_maps_mapvec():
    m = Map2D(1, 2, 3, 4)
    result = m.map(MapVec(5, 7))
    assert result == MapVec(1 * 5 + 2 * 7, 3 * 5 + 4 * 7)


def test_map2d_maps_duck_typed_vector():
    m = Map2D(1, 2, 3, 4)
    result = m.map(_VecLike(5, 7))
    assert result == MapVec(1 * 5 + 2 * 7, 3 * 5 + 4 * 7)


def test_map2d_compose():
    a = Map2D(1, 2, 3, 4)
    b = Map2D(5, 6, 7, 8)
    composed = a.compose(b)
    assert isinstance(composed, Map2D)
    # composed.map(v) should equal a.map(b.map(v)) for any vector v -- i.e.
    # compose produces the matrix product a @ b.
    v = MapVec(9, 11)
    assert composed.map(v) == a.map(b.map(v))


def test_map2d_identity_is_neutral_for_compose():
    identity = Map2D(1, 0, 0, 1)
    a = Map2D(2, 3, 4, 5)
    assert a.compose(identity) == a
    assert identity.compose(a) == a


def test_map2d_repr_and_equality():
    a = Map2D(1, 2, 3, 4)
    assert a == Map2D(1, 2, 3, 4)
    assert a != Map2D(1, 2, 3, 5)
    assert repr(a) == "Map2D(m00=1, m01=2, m10=3, m11=4)"


# --- TuningMap / EDOMap -------------------------------------------------


def test_tuning_map_constructor_raises_outside_fifth_bounds():
    TuningMap(700)
    # Boundaries are inclusive.
    TuningMap(1200 * 4 / 7)
    TuningMap(1200 * 3 / 5)
    # 600¢ (4-EDO's fifth): too narrow for a diatonic.
    with pytest.raises(ValueError):
        TuningMap(600)
    # 800¢ (3-EDO's fifth): too wide for a diatonic.
    with pytest.raises(ValueError):
        TuningMap(800)


def test_tuning_map_from_edo_raises_for_unsupported_edos():
    TuningMap.from_edo(12)
    TuningMap.from_edo(19)
    TuningMap.from_edo(31)
    # 5-EDO (720¢) and 7-EDO (~685.7¢) sit exactly on the boundaries.
    TuningMap.from_edo(5)
    TuningMap.from_edo(7)
    # 3-EDO (800¢) and 4-EDO (600¢) fall outside the range.
    with pytest.raises(ValueError):
        TuningMap.from_edo(3)
    with pytest.raises(ValueError):
        TuningMap.from_edo(4)


def test_edo_map_constructor_raises_for_unsupported_edos():
    EDOMap(12)
    EDOMap(31)
    EDOMap(5)
    EDOMap(7)
    with pytest.raises(ValueError):
        EDOMap(3)
    with pytest.raises(ValueError):
        EDOMap(4)


def test_edo_map_produces_correct_number():
    p = SPN.to_pitch("C4")
    t = EDOMap(12)
    assert t.to_number(p) == 60
    t = EDOMap(31)
    assert t.to_number(p) == 155


def test_edo_map_compares_pitches_correctly():
    p = SPN.to_pitch("C#4")
    q = SPN.to_pitch("Db4")
    t = EDOMap(12)
    assert t.compare(p, q) == 0
    t = EDOMap(31)
    assert t.compare(p, q) < 0
    t = EDOMap(53)
    assert t.compare(p, q) > 0


def test_tuning_map_to_hz_matches_known_reference_values():
    twelve_tet = TuningMap.from_edo(12)
    # Default reference is C4 = 261.6255653Hz -- so C4 itself should be exact.
    assert twelve_tet.to_hz(SPN.to_pitch("C4")) == pytest.approx(261.6255653)
    # This is precisely the constant from which A440 12TET tuning is derived.
    assert twelve_tet.to_hz(SPN.to_pitch("A4")) == pytest.approx(440.0)

    a440 = TuningMap.from_edo(12, "A4", 440)
    assert a440.to_hz(SPN.to_pitch("A4")) == pytest.approx(440.0)
    assert a440.to_hz(SPN.to_pitch("A5")) == pytest.approx(880.0)
    assert a440.to_hz(SPN.to_pitch("C4")) == pytest.approx(440.0 * 2 ** (-9 / 12))


def test_tuning_map_to_cents_and_to_ratio():
    twelve_tet = TuningMap.from_edo(12)
    octave = Interval.from_name("P8")
    assert twelve_tet.to_cents(octave) == pytest.approx(1200.0)
    assert twelve_tet.to_ratio(octave) == pytest.approx(2.0)

    unison = Interval.from_name("P1")
    assert twelve_tet.to_cents(unison) == pytest.approx(0.0)
    assert twelve_tet.to_ratio(unison) == pytest.approx(1.0)

    fifth = Interval.from_name("P5")
    assert twelve_tet.to_cents(fifth) == pytest.approx(700.0)


def test_pitch_audible_uses_tuning_map():
    t = TuningMap.from_edo(12, "A4", 440)

    # A4 (440Hz): comfortably within range.
    assert Pitch.audible(SPN.to_pitch("A4"), t)

    # C0 (~16.35Hz) and C-1 (~8.18Hz): below 20Hz.
    assert not Pitch.audible(SPN.to_pitch("C0"), t)
    assert not Pitch.audible(SPN.to_pitch("C-1"), t)

    # A0 (27.5Hz): just above 20Hz.
    assert Pitch.audible(SPN.to_pitch("A0"), t)

    # C10 (~16.7kHz): below 20kHz.
    assert Pitch.audible(SPN.to_pitch("C10"), t)

    # C11 (~33.5kHz): above 20kHz.
    assert not Pitch.audible(SPN.to_pitch("C11"), t)


def test_pitch_audible_falls_back_to_default_12_edo_tuning_map():
    # C4 at the default reference (C4 = 261.6255653Hz) is well within range.
    assert Pitch.audible(SPN.to_pitch("C4"))


def test_pitch_highest_and_lowest_use_tuning_map():
    pitches = [SPN.to_pitch(s) for s in ("C4", "G4", "Eb3", "C5")]
    assert SPN.from_pitch(Pitch.highest(pitches)) == "C5"
    assert SPN.from_pitch(Pitch.lowest(pitches)) == "Eb3"


def test_pitch_highest_and_lowest_break_ties_by_spelling():
    # C#4 and Db4 are enharmonic in 12TET -- steps_to breaks the tie.
    pitches = [SPN.to_pitch("C#4"), SPN.to_pitch("Db4")]
    assert SPN.from_pitch(Pitch.highest(pitches)) == "Db4"
    assert SPN.from_pitch(Pitch.lowest(pitches)) == "C#4"


def test_pitch_nearest_finds_closest_pitch():
    target = SPN.to_pitch("C4")
    candidates = [SPN.to_pitch(s) for s in ("E4", "G3", "Db4", "A4")]
    assert SPN.from_pitch(target.nearest(candidates)) == "Db4"


def test_pitch_nearest_does_not_mutate_input_list():
    target = SPN.to_pitch("C4")
    candidates = [SPN.to_pitch(s) for s in ("E4", "G3", "Db4", "A4")]
    original_order = [SPN.from_pitch(p) for p in candidates]
    target.nearest(candidates)
    assert [SPN.from_pitch(p) for p in candidates] == original_order
