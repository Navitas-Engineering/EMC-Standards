import os

from extraction import (
    choose_best_candidate,
    extract_pages,
    find_candidates,
    score_candidates
)

from extraction_continued import (
    build_filename,
    extract_designation_metadata,
    normalise_code
)

from filename_hint import extract_filename_hint
from validate_standard import validate_standard
from utils import StandardData


def process_file(file_path):
    """
    Process one PDF and return a StandardData result.

    A StandardData object is returned even when no candidate is found,
    so every PDF can be included in the review spreadsheet.
    """

    pages = extract_pages(file_path)

    total_text = "".join(
        page.get("text", "")
        for page in pages
    )

    extracted_text_length = len(total_text.strip())

    hint = extract_filename_hint(file_path)

    scores = score_candidates(pages)
    standard = choose_best_candidate(scores)

    # ------------------------------------------------------------
    # No candidate
    # ------------------------------------------------------------

    if standard is None:
        standard = StandardData(
            raw_code=None,
            source_filename=hint["source_filename"],
            filename_hint_code=hint["code"],
            filename_hint_year=hint["year"],
            filename_hint_amendment=hint["amendment"],
            filename_hint_amendment_year=hint["amendment_year"],
            status="NO_CANDIDATE",
            extracted_text_length=extracted_text_length
        )

        standard.add_reason("No standard code candidate found")

        if extracted_text_length == 0:
            standard.add_reason("No extractable text")

        elif extracted_text_length < 100:
            standard.add_reason(
                "Very little extractable text; PDF may require manual review"
            )

        return validate_standard(standard)

    # ------------------------------------------------------------
    # Store filename hints
    # ------------------------------------------------------------

    standard.source_filename = hint["source_filename"]
    standard.filename_hint_code = hint["code"]
    standard.filename_hint_year = hint["year"]
    standard.filename_hint_amendment = hint["amendment"]
    standard.filename_hint_amendment_year = hint["amendment_year"]
    standard.extracted_text_length = extracted_text_length

    # ------------------------------------------------------------
    # Normalise the extracted code
    # ------------------------------------------------------------

    standard.normalised_code = normalise_code(
        standard.raw_code
    )

    # ------------------------------------------------------------
    # Extract year and amendment metadata
    # ------------------------------------------------------------

    metadata = extract_designation_metadata(
        pages,
        standard.raw_code
    )

    standard.year = metadata["year"]
    standard.amendment = metadata["amendment"]
    standard.amendment_year = metadata["amendment_year"]

    # ------------------------------------------------------------
    # Controlled BR exception
    # ------------------------------------------------------------

    if (
        standard.normalised_code
        and standard.normalised_code.startswith("BR_")
        and standard.year is not None
        and standard.year > 2000
    ):
        original_year = standard.year
        standard.year = 0

        standard.add_reason(
            f"BR year {original_year} appears suspicious and was reset to 0"
        )

    # ------------------------------------------------------------
    # Amendment sanity check
    # ------------------------------------------------------------

    if (
        standard.amendment_year is not None
        and standard.year is not None
        and standard.year != 0
        and standard.amendment_year < standard.year
    ):
        invalid_amendment = standard.amendment
        invalid_amendment_year = standard.amendment_year

        standard.amendment = None
        standard.amendment_year = None

        standard.add_reason(
            "Invalid amendment removed "
            f"({invalid_amendment} {invalid_amendment_year} "
            f"is before publication year {standard.year})"
        )

    # ------------------------------------------------------------
    # Build proposed filename
    # ------------------------------------------------------------

    if standard.normalised_code:
        standard.filename = build_filename(standard)

        standard.proposed_path = os.path.join(
            os.path.dirname(file_path),
            standard.filename + ".pdf"
        )

    # ------------------------------------------------------------
    # Validate against current filename and extracted metadata
    # ------------------------------------------------------------

    standard = validate_standard(standard)

    return standard


def test_single_file(file_path):
    """
    Display detailed processing output for one PDF.
    """

    print("\n" + "=" * 80)
    print(f"Testing file: {file_path}")

    pages = extract_pages(file_path)
    scores = score_candidates(pages)

    print(f"Scores: {scores}")

    standard = process_file(file_path)

    print(f"Result: {standard}")
    print(f"Status: {standard.status}")
    print(f"Reasons: {standard.reasons_text()}")

    if standard.raw_code is None:
        print("Dumping page text and candidates for debugging:")

        for page_data in pages:
            page_no = page_data["page"]
            page_text = page_data["text"]

            print(f"\nPage {page_no}")
            print(page_text)

            candidates = find_candidates(page_text)

            print("Candidates:")
            for candidate in candidates:
                print(candidate)