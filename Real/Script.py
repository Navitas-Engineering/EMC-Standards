import os
import pandas as pd

from extraction import get_file_names
from processing import process_file, test_single_file
from extraction_continued import rename_file


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

DRY_RUN = True
EXPORT_RESULTS = True

DIRECTORY = r"Test Docs"

RESULTS_WORKBOOK = "RenameResults.xlsx"


# ------------------------------------------------------------
# Processing
# ------------------------------------------------------------

sample_list = get_file_names(DIRECTORY)

results = []

print("Found files:")

for file_path in sample_list:
    print(file_path)

print("\nProcessing...\n")


for file_path in sample_list:

    try:
        standard = process_file(file_path)

    except Exception as error:
        print(
            f"Processing failed for {file_path}: "
            f"{type(error).__name__}: {error}"
        )

        results.append(
            {
                "Original File": file_path,
                "Source Filename": os.path.basename(file_path),
                "Filename Hint Code": None,
                "Filename Hint Year": None,
                "Raw Code": None,
                "Normalised Code": None,
                "Extracted Year": None,
                "Amendment": None,
                "Amendment Year": None,
                "Score": 0,
                "Extracted Text Length": 0,
                "Generated Filename": None,
                "Proposed Path": None,
                "Status": "REVIEW_REQUIRED",
                "Reasons": (
                    f"Processing error: "
                    f"{type(error).__name__}: {error}"
                ),
                "Rename Result": "Not renamed"
            }
        )

        continue

    proposed_path = standard.proposed_path

    print(
        f"{file_path}\n"
        f"  Proposed filename: {standard.filename}\n"
        f"  Status: {standard.status}\n"
        f"  Reasons: {standard.reasons_text() or 'None'}"
    )

    # Default result until rename logic runs.
    rename_result = "Not renamed"

    # --------------------------------------------------------
    # Dry run
    # --------------------------------------------------------

    if DRY_RUN:

        if (
            standard.status == "SUCCESS"
            and proposed_path
        ):
            rename_result = "Dry run - would rename"

            print(
                "  Would rename:\n"
                f"    {file_path}\n"
                "  to:\n"
                f"    {proposed_path}"
            )

        else:
            rename_result = (
                f"Dry run - not eligible because status is "
                f"{standard.status}"
            )

            print(
                "  Would not rename automatically."
            )

    # --------------------------------------------------------
    # Real rename
    # --------------------------------------------------------

    else:

        # Only SUCCESS records are eligible for automatic renaming.
        if (
            standard.status == "SUCCESS"
            and standard.filename
        ):
            success, message = rename_file(
                file_path,
                standard
            )

            rename_result = message

            if success:
                print(f"  Rename result: {message}")

            else:
                standard.status = "REVIEW_REQUIRED"
                standard.add_reason(message)

                print(f"  Rename failed: {message}")

        else:
            rename_result = (
                f"Not renamed because status is "
                f"{standard.status}"
            )

            print(
                "  Not renamed automatically."
            )

    standard.rename_result = rename_result

    # --------------------------------------------------------
    # Add every file to the review report
    # --------------------------------------------------------

    results.append(
        {
            "Original File": file_path,
            "Source Filename": standard.source_filename,
            "Filename Hint Code": standard.filename_hint_code,
            "Filename Hint Year": standard.filename_hint_year,
            "Filename Hint Amendment":
                standard.filename_hint_amendment,
            "Filename Hint Amendment Year":
                standard.filename_hint_amendment_year,
            "Raw Code": standard.raw_code,
            "Normalised Code": standard.normalised_code,
            "Extracted Year": standard.year,
            "Amendment": standard.amendment,
            "Amendment Year": standard.amendment_year,
            "Score": standard.score,
            "Extracted Text Length":
                standard.extracted_text_length,
            "Generated Filename": standard.filename,
            "Proposed Path": proposed_path,
            "Status": standard.status,
            "Reasons": standard.reasons_text(),
            "Rename Result": rename_result
        }
    )

    print()


# ------------------------------------------------------------
# Build final report
# ------------------------------------------------------------

final_list = pd.DataFrame(results)

print("\nFinal List:")
print(final_list)

print("\nStatus Summary:")

if not final_list.empty:
    print(
        final_list["Status"].value_counts(
            dropna=False
        )
    )


# ------------------------------------------------------------
# Export results
# ------------------------------------------------------------

# As requested, export after a real run.
if EXPORT_RESULTS:

    summary = (
        final_list["Status"]
        .value_counts(dropna=False)
        .rename_axis("Status")
        .reset_index(name="Count")
    )

    review_items = final_list[
        final_list["Status"] != "SUCCESS"
    ].copy()

    with pd.ExcelWriter(
        RESULTS_WORKBOOK,
        engine="openpyxl"
    ) as writer:

        final_list.to_excel(
            writer,
            sheet_name="All Results",
            index=False
        )

        review_items.to_excel(
            writer,
            sheet_name="Review Required",
            index=False
        )

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

    print(
        f"\nResults exported to: "
        f"{os.path.abspath(RESULTS_WORKBOOK)}"
    )



# ------------------------------------------------------------
# Optional targeted debugging
# ------------------------------------------------------------

# Uncomment these when you specifically want detailed debugging.

# test_single_file(
#     r"Test Docs\Documents\NR_L2_ELP_27716-01_2023.pdf"
# )

# test_single_file(
#     r"Test Docs\Documents\EN_50238-3_2013.pdf"
# )

# test_single_file(
#     r"Test Docs\Documents\IEC_61000-1-2_2001.pdf"
# )