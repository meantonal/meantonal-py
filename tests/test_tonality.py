from meantonal import SPN, TonalContext


def test_from_strings_creates_correct_context():
    context = TonalContext.from_strings("Eb", "Phrygian")
    assert context.mode == 5
    assert context.tonic.letter == "E"
    assert context.tonic.accidental == -1
    assert context.tonic.chroma == -3


def test_degree_number_produces_correct_result():
    context = TonalContext(0, 1)
    assert SPN.to_pitch("C4").degree_in(context) == 0
    assert SPN.to_pitch("D4").degree_in(context) == 1
    assert SPN.to_pitch("E4").degree_in(context) == 2
    assert SPN.to_pitch("F4").degree_in(context) == 3
    assert SPN.to_pitch("G4").degree_in(context) == 4
    assert SPN.to_pitch("A4").degree_in(context) == 5
    assert SPN.to_pitch("B4").degree_in(context) == 6
    assert SPN.to_pitch("C#4").degree_in(context) == 0
    p = SPN.to_pitch("Db4")
    assert p.degree_in(context) == 1
    context = TonalContext(0, 5)
    assert p.degree_in(context) == 1


def test_degree_alteration_produces_correct_result():
    context = TonalContext(0, 1)
    assert SPN.to_pitch("C4").alteration_in(context) == 0
    assert SPN.to_pitch("C#4").alteration_in(context) == 1
    assert SPN.to_pitch("Cb4").alteration_in(context) == -2
    assert SPN.to_pitch("Db4").alteration_in(context) == -1
    assert SPN.to_pitch("E#4").alteration_in(context) == 2
    context = TonalContext(0, 4)
    assert SPN.to_pitch("Cb4").alteration_in(context) == -1
    assert SPN.to_pitch("A#4").alteration_in(context) == 2


def test_degree_chroma_produces_correct_result():
    context = TonalContext(1, 4)
    assert context.degree_chroma(0) == 1
    assert context.degree_chroma(1) == 3
    assert context.degree_chroma(2) == -2
    assert context.degree_chroma(3) == 0
    assert context.degree_chroma(4) == 2
    assert context.degree_chroma(5) == -3
    assert context.degree_chroma(6) == -1
    assert context.degree_chroma(3, 1) == 7
    assert context.degree_chroma(3, -1) == -7
    assert context.degree_chroma(3, 3) == 21


def test_snap_diatonic_produces_correct_result():
    context = TonalContext(2, 1)
    q = SPN.to_pitch("E4")
    p = SPN.to_pitch("Eb4")
    assert p.snap_to(context).is_equal(q)
    p = SPN.to_pitch("E#4")
    assert p.snap_to(context).is_equal(q)
    p = SPN.to_pitch("Bb4")
    q = SPN.to_pitch("B4")
    assert p.snap_to(context).is_equal(q)


def test_transpose_diatonic_produces_correct_result():
    context = TonalContext(2, 1)
    p = SPN.to_pitch("D4")
    q = SPN.to_pitch("E4")
    assert p.transpose_diatonic(1, context).is_equal(q)
    p = SPN.to_pitch("D#4")
    assert p.transpose_diatonic(1, context).is_equal(q)
    q = SPN.to_pitch("A3")
    assert p.transpose_diatonic(-3, context).is_equal(q)
