from meantonal import Chroma


def test_to_letter_matches_circle_of_fifths():
    # C(0) G(1) D(2) A(3) E(4) B(5) F(6, i.e. F#) ... wraps back through the letters.
    assert Chroma.to_letter(0) == "C"
    assert Chroma.to_letter(1) == "G"
    assert Chroma.to_letter(2) == "D"
    assert Chroma.to_letter(3) == "A"
    assert Chroma.to_letter(4) == "E"
    assert Chroma.to_letter(5) == "B"
    assert Chroma.to_letter(6) == "F"
    assert Chroma.to_letter(-1) == "F"


def test_to_letter_handles_negative_and_large_chroma():
    # to_letter is periodic mod 7 in chroma: -6 == 1 (mod 7) -> same letter as chroma=1.
    assert Chroma.to_letter(-6) == "G"
    assert Chroma.to_letter(7) == "C"
    assert Chroma.to_letter(-7) == "C"


def test_to_accidental_natural_range():
    # The natural (accidental == 0) window spans 7 consecutive chroma values.
    for chroma in range(-1, 6):
        assert Chroma.to_accidental(chroma) == 0


def test_to_accidental_sharp_and_flat():
    assert Chroma.to_accidental(6) == 1  # sharp family starts here
    assert Chroma.to_accidental(-2) == -1  # flat family starts here
    assert Chroma.to_accidental(13) == 2  # double sharp family starts here
    assert Chroma.to_accidental(-9) == -2  # double flat family starts here
