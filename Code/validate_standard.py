from filename_hint import filename_contains_code


def validate_standard(standard):
    """
    Validate extracted information and decide whether the file can be
    safely renamed automatically.

    The current filename is treated as a hint, not as the source of
    truth.
    """

    # Preserve reasons already added during processing.
    if standard.reasons is None:
        standard.reasons = []

    # A no-candidate result has its own status.
    if standard.raw_code is None:
        standard.status = "NO_CANDIDATE"
        standard.add_reason("No standard code candidate found")
        return standard

    standard.status = "SUCCESS"

    # ------------------------------------------------------------
    # 1. Basic extracted-data checks
    # ------------------------------------------------------------

    if not standard.normalised_code:
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason("No normalised standard code produced")

    if standard.year is None:
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason("No publication year found")

    if standard.year == 0:
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason("Publication year requires manual review")

    # BR documents should not normally resolve to a modern year.
    if (
        standard.normalised_code
        and standard.normalised_code.startswith("BR_")
        and standard.year == 0
    ):
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason("Suspicious BR publication year")

    # Very small amounts of extracted text usually indicate an
    # image-only or otherwise difficult PDF.
    if standard.extracted_text_length == 0:
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason("No extractable text")

    elif standard.extracted_text_length < 100:
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason(
            "Very little extractable text; PDF may require manual review"
        )

    # ------------------------------------------------------------
    # 2. Filename code comparison
    # ------------------------------------------------------------

    if (
        standard.source_filename
        and standard.normalised_code
    ):
        code_found_in_filename = filename_contains_code(
            standard.source_filename,
            standard.normalised_code
        )

        if not code_found_in_filename:
            standard.status = "REVIEW_REQUIRED"
            standard.add_reason(
                "Extracted code is not contained in current filename "
                f"({standard.normalised_code})"
            )

    # ------------------------------------------------------------
    # 3. Filename year comparison
    # ------------------------------------------------------------

    if (
        standard.filename_hint_year is not None
        and standard.year is not None
        and standard.year != 0
        and standard.filename_hint_year != standard.year
    ):
        standard.status = "REVIEW_REQUIRED"

        difference = abs(
            standard.filename_hint_year - standard.year
        )

        standard.add_reason(
            "Publication year differs from filename hint "
            f"({standard.filename_hint_year} vs {standard.year})"
        )

        if difference > 3:
            standard.add_reason(
                f"Large publication-year difference ({difference} years)"
            )

    # ------------------------------------------------------------
    # 4. Amendment comparison
    # ------------------------------------------------------------

    if (
        standard.filename_hint_amendment
        and standard.amendment
        and standard.filename_hint_amendment != standard.amendment
    ):
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason(
            "Amendment differs from filename hint "
            f"({standard.filename_hint_amendment} "
            f"vs {standard.amendment})"
        )

    if (
        standard.filename_hint_amendment_year is not None
        and standard.amendment_year is not None
        and standard.filename_hint_amendment_year
        != standard.amendment_year
    ):
        standard.status = "REVIEW_REQUIRED"
        standard.add_reason(
            "Amendment year differs from filename hint "
            f"({standard.filename_hint_amendment_year} "
            f"vs {standard.amendment_year})"
        )

    # The extracted candidate score is useful in the report.
    # Do not add an arbitrary low-score rule until you have inspected
    # the score distribution from a complete run.

    return standard
