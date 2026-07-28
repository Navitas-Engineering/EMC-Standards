from pathlib import Path

import pytest

from extraction import (
    choose_best_candidate,
    extract_pages,
    score_candidates
)

from processing import process_file


TESTS_DIRECTORY = Path(__file__).resolve().parent
AUTOMATION_DIRECTORY = TESTS_DIRECTORY.parent

DLR_TEST_FILE = (
    AUTOMATION_DIRECTORY
    / "Standards"
    / "Sample Documents"
    / "DLR_ENG_STD_ES102_2012.pdf"
)


@pytest.fixture(scope="module")
def dlr_standard():
    """
    Process the DLR sample once for all tests in this module.
    """

    if not DLR_TEST_FILE.exists():
        pytest.skip(
            f"Sample PDF not found: {DLR_TEST_FILE}"
        )

    return process_file(
        str(DLR_TEST_FILE)
    )


def test_dlr_sample_produces_expected_filename(
    dlr_standard
):
    assert (
        dlr_standard.filename
        == "DLR_ENG_STD_ES102_2012"
    )


def test_dlr_sample_contains_expected_code_components(
    dlr_standard
):
    filename = dlr_standard.filename or ""

    expected_components = [
        "DLR",
        "ENG",
        "STD",
        "ES102"
    ]

    for component in expected_components:
        assert component in filename, (
            f"Expected {component!r} in generated filename, "
            f"but got {filename!r}"
        )


def test_dlr_sample_has_normalised_code(
    dlr_standard
):
    assert (
        dlr_standard.normalised_code
        == "DLR_ENG_STD_ES102"
    )


def test_dlr_sample_extracts_expected_year(
    dlr_standard
):
    assert dlr_standard.year == 2012


def test_extract_pages_from_real_pdf():
    if not DLR_TEST_FILE.exists():
        pytest.skip(
            f"Sample PDF not found: {DLR_TEST_FILE}"
        )

    pages = extract_pages(
        str(DLR_TEST_FILE)
    )

    assert pages
    assert len(pages) <= 5

    for page in pages:
        assert "page" in page
        assert "text" in page


def test_real_pdf_produces_candidate_scores():
    if not DLR_TEST_FILE.exists():
        pytest.skip(
            f"Sample PDF not found: {DLR_TEST_FILE}"
        )

    pages = extract_pages(
        str(DLR_TEST_FILE)
    )

    scores = score_candidates(pages)

    assert isinstance(scores, dict)
    assert scores


def test_real_pdf_produces_best_candidate():
    if not DLR_TEST_FILE.exists():
        pytest.skip(
            f"Sample PDF not found: {DLR_TEST_FILE}"
        )

    pages = extract_pages(
        str(DLR_TEST_FILE)
    )

    scores = score_candidates(pages)
    best_candidate = choose_best_candidate(scores)

    assert best_candidate is not None
    assert best_candidate.raw_code is not None