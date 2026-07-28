import pytest

from extraction_continued import (
    build_filename,
    normalise_code
)
from utils import StandardData


@pytest.mark.parametrize(
    ("raw_code", "expected"),
    [
        ("GEGN8646", "GEGN_8646"),
        ("GEGN 8646", "GEGN_8646"),
        ("GE/GN/8646", "GEGN_8646"),
        ("GE_GN_8646", "GEGN_8646"),
        ("GE-GN-8646", "GEGN_8646"),
        ("GE GN 8646", "GEGN_8646"),
        ("gegn8646", "GEGN_8646"),
        ("GLGN1620", "GLGN_1620"),
        ("GLGN 1620", "GLGN_1620"),
        ("GL/GN/1620", "GLGN_1620"),
        ("GL_GN_1620", "GLGN_1620"),
        ("GL-GN-1620", "GLGN_1620"),
        ("GL GN 1620", "GLGN_1620"),
        ("glgn1620", "GLGN_1620"),
    ]
)
def test_normalise_guidance_note_codes(
    raw_code,
    expected
):
    assert normalise_code(raw_code) == expected


@pytest.mark.parametrize(
    ("raw_code", "expected"),
    [
        ("GE/RT/8270", "GE_RT_8270"),
        ("GM/RC1500", "GM_RC_1500"),
        (
            "NR/L2/ELP/27716/01",
            "NR_L2_ELP_27716-01"
        ),
        ("BS EN 55032", "EN_55032"),
        ("IEC 61439-1", "IEC_61439-1"),
        ("BR 13422", "BR_13422"),
    ]
)
def test_guidance_note_change_does_not_break_other_codes(
    raw_code,
    expected
):
    assert normalise_code(raw_code) == expected


@pytest.mark.parametrize(
    (
        "raw_code",
        "year",
        "expected_filename"
    ),
    [
        (
            "GE/GN/8646",
            2017,
            "GEGN_8646_2017"
        ),
        (
            "GL/GN/1620",
            2024,
            "GLGN_1620_2024"
        ),
    ]
)
def test_build_guidance_note_filename(
    raw_code,
    year,
    expected_filename
):
    standard = StandardData(
        raw_code=raw_code,
        normalised_code=normalise_code(
            raw_code
        ),
        year=year
    )

    assert (
        build_filename(standard)
        == expected_filename
    )