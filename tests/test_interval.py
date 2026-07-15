import pytest

from meantonal import Interval, Pitch


def test_from_name_creates_correct_interval_vector():
    m = Interval.from_name("P5")
    assert (m.w, m.h) == (3, 1)
    m = Interval.from_name("5")
    assert (m.w, m.h) == (3, 1)
    m = Interval.from_name("d5")
    assert (m.w, m.h) == (2, 2)
    m = Interval.from_name("b5")
    assert (m.w, m.h) == (2, 2)
    m = Interval.from_name("A5")
    assert (m.w, m.h) == (4, 0)
    m = Interval.from_name("#5")
    assert (m.w, m.h) == (4, 0)
    m = Interval.from_name("M3")
    assert (m.w, m.h) == (2, 0)
    m = Interval.from_name("3")
    assert (m.w, m.h) == (2, 0)
    m = Interval.from_name("m3")
    assert (m.w, m.h) == (1, 1)
    m = Interval.from_name("b3")
    assert (m.w, m.h) == (1, 1)


def test_from_name_raises_for_invalid_name():
    with pytest.raises(ValueError):
        Interval.from_name("not-an-interval")


def test_between_creates_correct_interval_vector():
    p = Pitch.from_chroma(0, 4)  # C4
    q = Pitch.from_chroma(4, 4)  # E4
    assert Interval.between(p, q) == Interval.from_name("M3")


def test_chroma_produces_correct_result():
    m = Interval.from_name("M3")
    assert m.chroma == 4
    m = Interval.from_name("m3")
    assert m.chroma == -3
    m = Interval.from_name("A6")
    assert m.chroma == 10


def test_is_diatonic_produces_correct_result():
    for name in (
        "P1",
        "m2",
        "M2",
        "m3",
        "M3",
        "P4",
        "A4",
        "d5",
        "P5",
        "m6",
        "M6",
        "m7",
        "M7",
        "P8",
    ):
        assert Interval.from_name(name).is_diatonic
    for name in ("d3", "A6", "A5"):
        assert not Interval.from_name(name).is_diatonic


def test_is_tonal_produces_correct_result():
    for name in (
        "P1",
        "m2",
        "M2",
        "m3",
        "M3",
        "P4",
        "A4",
        "d5",
        "P5",
        "m6",
        "M6",
        "m7",
        "M7",
        "P8",
        "d3",
        "A6",
        "A5",
        "AA2",
    ):
        assert Interval.from_name(name).is_tonal
    for name in ("AA6", "dd3", "AAA5"):
        assert not Interval.from_name(name).is_tonal


def test_quality_produces_correct_result():
    for name in ("P1", "P8", "P5", "P4"):
        assert Interval.from_name(name).quality == 0
    for name in ("M2", "M6", "M3", "M7"):
        assert Interval.from_name(name).quality == 1
    for name in ("m7", "m3", "m6", "m2"):
        assert Interval.from_name(name).quality == -1
    for name in ("A4", "A1", "A5", "A2", "A6", "A3", "A7"):
        assert Interval.from_name(name).quality == 2
    for name in ("d4", "d1", "d5", "d2", "d6", "d3", "d7"):
        assert Interval.from_name(name).quality == -2
    assert Interval.from_name("AA4").quality == 3
    assert Interval.from_name("dd4").quality == -3
    assert Interval.from_name("dd6").quality == -3


def test_stepspan_produces_correct_result():
    for name in ("A6", "M6", "m6", "d6"):
        assert Interval.from_name(name).stepspan == 5
    assert Interval.from_name("m13").stepspan == 12


def test_pc7_produces_correct_result():
    assert Interval.from_name("M6").pc7 == 5
    assert Interval.from_name("m13").pc7 == 5
    assert Interval.from_name("P8").pc7 == 0


def test_pc12_produces_correct_result():
    assert Interval.from_name("M3").pc12 == 4
    assert Interval.from_name("A4").pc12 == 6
    assert Interval.from_name("M7").pc12 == 11
    assert Interval.from_name("M9").pc12 == 2
    assert Interval.from_name("P8").pc12 == 0


def test_name_round_trips():
    for name in ("AA5", "A5", "P5", "d5", "dd5", "A6", "M6", "m6", "d6", "dd6"):
        assert Interval.from_name(name).name == name


def test_is_equal_produces_correct_result():
    m = Interval(2, 0)
    n = Interval(1, 1)
    assert not m.is_equal(n)
    n = Interval(2, 0)
    assert m.is_equal(n)


def test_is_enharmonic_produces_correct_result():
    m = Interval.from_name("m7")
    n = Interval.from_name("A6")
    assert m.is_enharmonic(n)
    assert not m.is_enharmonic(n, 31)
    m = Interval.from_name("P8")
    n = Interval.from_name("AAAA6")
    assert m.is_enharmonic(n, 31)
    assert not m.is_enharmonic(n)


def test_negative_produces_correct_result():
    m = Interval(3, 4)
    n = Interval(-3, -4)
    assert m.negative.is_equal(n)


def test_add_produces_correct_result():
    m = Interval.from_name("M3")
    n = Interval.from_name("m3")
    total = Interval.from_name("P5")
    assert m.add(n).is_equal(total)


def test_subtract_produces_correct_result():
    m = Interval.from_name("P5")
    n = Interval.from_name("m3")
    difference = Interval.from_name("M3")
    assert m.subtract(n).is_equal(difference)


def test_times_produces_correct_result():
    m = Interval.from_name("P5")
    n = Interval.from_name("M13")
    assert m.times(3).is_equal(n)


def test_simple_produces_correct_result():
    m = Interval.from_name("M17")
    n = Interval.from_name("M3")
    assert m.simple.is_equal(n)
    assert m.negative.simple.is_equal(n.negative)


def test_range_diatonic_produces_correct_range():
    from_ = Interval.from_name("P1")
    to = Interval.from_name("P8")
    names = [m.name for m in Interval.range.diatonic(from_, to)]
    for expected in (
        "P1",
        "m2",
        "M2",
        "m3",
        "M3",
        "P4",
        "A4",
        "d5",
        "P5",
        "m6",
        "M6",
        "m7",
        "M7",
        "P8",
    ):
        assert expected in names
    for unexpected in ("A5", "-m2", "m9", "M9"):
        assert unexpected not in names

    from_ = Interval.from_name("M3")
    to = Interval.from_name("M10")
    names = [m.name for m in Interval.range.diatonic(from_, to)]
    for unexpected in ("P1", "m2", "M2", "m3"):
        assert unexpected not in names
    for expected in (
        "M3",
        "P4",
        "A4",
        "d5",
        "P5",
        "m6",
        "M6",
        "m7",
        "M7",
        "P8",
        "m9",
        "M9",
        "m10",
        "M10",
    ):
        assert expected in names
    for unexpected in ("A5", "-m2", "P11"):
        assert unexpected not in names


def test_range_diatonic_defaults_to_a_single_octave():
    names = [m.name for m in Interval.range.diatonic()]
    assert "P1" in names
    assert "P8" in names
    assert "M9" not in names


def test_operator_add_matches_add_method():
    m = Interval.from_name("M3")
    n = Interval.from_name("m3")
    assert m + n == Interval.from_name("P5")
    assert m + n == m.add(n)


def test_operator_sub_matches_subtract_method():
    m = Interval.from_name("P5")
    n = Interval.from_name("m3")
    assert m - n == Interval.from_name("M3")
    assert m - n == m.subtract(n)


def test_operator_neg_matches_negative_property():
    m = Interval(3, 4)
    assert -m == Interval(-3, -4)
    assert -m == m.negative


def test_operator_mul_matches_times_method():
    m = Interval.from_name("P5")
    assert m * 3 == Interval.from_name("M13")
    assert 3 * m == Interval.from_name("M13")
    assert m * 3 == m.times(3)


def test_operators_reject_unsupported_types():
    m = Interval.from_name("P5")
    with pytest.raises(TypeError):
        m + 1
    with pytest.raises(TypeError):
        m - 1
    with pytest.raises(TypeError):
        m * 1.5


def test_range_melodic_produces_correct_range():
    names = [m.name for m in Interval.range.melodic()]
    for expected in ("P1", "m2", "M2", "m3", "M3", "P4", "P5", "m6", "M6", "P8"):
        assert expected in names
    for unexpected in ("A4", "d5", "m7", "M7", "A5", "-m2", "m9", "M9"):
        assert unexpected not in names
