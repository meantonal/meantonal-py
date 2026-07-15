from meantonal import (
    GENERATORS_FROM,
    GENERATORS_TO,
    LETTER_COORDS,
    MODES,
    WICKI_FROM,
    WICKI_TO,
    Map2D,
)


def test_modes_lookup():
    assert MODES["LYDIAN"] == 0
    assert MODES["IONIAN"] == 1
    assert MODES["MIXOLYDIAN"] == 2
    assert MODES["DORIAN"] == 3
    assert MODES["AEOLIAN"] == 4
    assert MODES["PHRYGIAN"] == 5
    assert MODES["LOCRIAN"] == 6
    assert MODES["MAJOR"] == MODES["IONIAN"]
    assert MODES["MINOR"] == MODES["AEOLIAN"]


def test_letter_coords_matches_letter_order():
    assert len(LETTER_COORDS) == 7
    assert LETTER_COORDS[0] == (0, 0)  # C
    assert LETTER_COORDS[1] == (1, 0)  # D
    assert LETTER_COORDS[2] == (2, 0)  # E
    assert LETTER_COORDS[3] == (2, 1)  # F
    assert LETTER_COORDS[4] == (3, 1)  # G
    assert LETTER_COORDS[5] == (4, 1)  # A
    assert LETTER_COORDS[6] == (5, 1)  # B


def test_wicki_and_generators_are_map2d_instances():
    for m in (WICKI_TO, WICKI_FROM, GENERATORS_TO, GENERATORS_FROM):
        assert isinstance(m, Map2D)


def test_generators_to_and_from_are_inverses():
    from meantonal import MapVec

    v = MapVec(11, 4)
    round_tripped = GENERATORS_FROM.map(GENERATORS_TO.map(v))
    assert round_tripped == v
