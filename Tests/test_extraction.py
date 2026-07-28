from collections import defaultdict

import pytest

from extraction import (
    canonicalise_candidate,
    choose_best_candidate,
    find_candidates,
    score_candidates
)


@pytest.mark.parametrize(
    ("candidate", "expected"),
    [
        ("GEGN8646", "GEGN 8646"),
        ("GEGN 8646", "GEGN 8646"),
        ("GE/GN/8646", "GEGN 8646"),
        ("GE_GN_8646", "GEGN 8646"),
        ("GE-GN-8646", "GEGN 8646"),
        ("GE GN 8646", "GEGN 8646"),
        ("gegn8646", "GEGN 8646"),
        ("GLGN1620", "GLGN 1620"),
        ("GLGN 1620", "GLGN 1620"),
        ("GL/GN/1620", "GLGN 1620"),
        ("GL_GN_1620", "GLGN 1620"),
        ("GL-GN-1620", "GLGN 1620"),
        ("GL GN 1620", "GLGN 1620"),
        ("glgn1620", "GLGN 1620"),
    ]
)
def test_canonicalise_guidance_note_candidate(
    candidate,
    expected
):
    assert canonicalise_candidate(candidate) == expected


@pytest.mark.parametrize(
    "candidate",
    [
        "GE/RT/8270",
        "GM/RC1500",
        "NR/L2/ELP/27716-01",
        "EN 55032",
        "IEC 61439-1",
        "BR 13422",
    ]
)
def test_canonicalise_candidate_does_not_change_other_codes(
    candidate
):
    assert canonicalise_candidate(candidate) == candidate.upper()


@pytest.mark.parametrize(
    ("page_text", "expected_candidate"),
    [
        ("GEGN8646", "GEGN8646"),
        ("GEGN 8646", "GEGN 8646"),
        ("GE/GN/8646", "GE/GN/8646"),
        ("GE_GN_8646", "GE_GN_8646"),
        ("GE-GN-8646", "GE-GN-8646"),
        ("GE GN 8646", "GE GN 8646"),
        ("GLGN1620", "GLGN1620"),
        ("GLGN 1620", "GLGN 1620"),
        ("GL/GN/1620", "GL/GN/1620"),
        ("GL_GN_1620", "GL_GN_1620"),
    ]
)
def test_find_candidates_detects_guidance_note_variants(
    page_text,
    expected_candidate
):
    candidates = find_candidates(page_text)

    candidate_values = [
        candidate
        for candidate, _ in candidates
    ]

    assert expected_candidate in candidate_values


def test_score_candidates_combines_equivalent_gegn_variants():
    pages = [
        {
            "page": 1,
            "text": (
                "GEGN8646\n"
                "This document is also designated GE/GN/8646."
            )
        }
    ]

    scores = score_candidates(pages)

    assert "GEGN 8646" in scores

    assert "GEGN8646" not in scores
    assert "GE/GN/8646" not in scores


def test_score_candidates_combines_equivalent_glgn_variants():
    pages = [
        {
            "page": 1,
            "text": (
                "GLGN1620\n"
                "Document designation GL/GN/1620."
            )
        }
    ]

    scores = score_candidates(pages)

    assert "GLGN 1620" in scores

    assert "GLGN1620" not in scores
    assert "GL/GN/1620" not in scores


def test_choose_best_candidate_returns_standard_data():
    scores = defaultdict(
        int,
        {
            "GEGN 8646": 1000,
            "GE/RT/8270": 500
        }
    )

    standard = choose_best_candidate(scores)

    assert standard is not None
    assert standard.raw_code == "GEGN 8646"
    assert standard.score == 1000


def test_choose_best_candidate_returns_none_for_empty_scores():
    assert choose_best_candidate({}) is None
