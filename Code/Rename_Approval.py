from pathlib import Path
import os

import pandas as pd


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

DRY_RUN = True

CODE_DIRECTORY = Path(__file__).resolve().parent
AUTOMATION_DIRECTORY = CODE_DIRECTORY.parent

RESULTS_WORKBOOK = (
    AUTOMATION_DIRECTORY
    / f"RenameResults_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
)


# ------------------------------------------------------------
# Load reviewed results
# ------------------------------------------------------------

if not RESULTS_WORKBOOK.exists():
    raise FileNotFoundError(
        "The reviewed results workbook could not be found:\n"
        f"{RESULTS_WORKBOOK}"
    )


results = pd.read_excel(
    RESULTS_WORKBOOK,
    sheet_name="All Results",
    engine="openpyxl"
)


required_columns = [
    "Original File",
    "Generated Filename",
    "Status",
    "Manual Decision",
    "Approved Filename"
]


missing_columns = [
    column
    for column in required_columns
    if column not in results.columns
]


if missing_columns:
    raise ValueError(
        "The workbook is missing required columns: "
        + ", ".join(missing_columns)
    )


# ------------------------------------------------------------
# Select approved records
# ------------------------------------------------------------

results["Manual Decision"] = (
    results["Manual Decision"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
)


approved_rows = results[
    results["Manual Decision"] == "APPROVE"
].copy()


print(
    f"Found {len(approved_rows)} manually approved records."
)


# ------------------------------------------------------------
# Apply approved renames
# ------------------------------------------------------------

for index, row in approved_rows.iterrows():

    source_path = Path(
        str(row["Original File"])
    )

    approved_filename = row.get(
        "Approved Filename"
    )

    generated_filename = row.get(
        "Generated Filename"
    )

    if (
        pd.notna(approved_filename)
        and str(approved_filename).strip()
    ):
        final_filename = str(
            approved_filename
        ).strip()

    elif (
        pd.notna(generated_filename)
        and str(generated_filename).strip()
    ):
        final_filename = str(
            generated_filename
        ).strip()

    else:
        print(
            f"SKIPPED: No filename supplied for {source_path}"
        )
        continue

    # Remove .pdf if the reviewer entered it.
    if final_filename.lower().endswith(".pdf"):
        final_filename = final_filename[:-4]

    destination_path = (
        source_path.parent
        / f"{final_filename}.pdf"
    )

    print()
    print(f"Approved source: {source_path}")
    print(f"Approved target: {destination_path}")

    if not source_path.exists():
        print("SKIPPED: Source file does not exist")
        continue

    if source_path.suffix.lower() != ".pdf":
        print("SKIPPED: Source is not a PDF")
        continue

    if (
        os.path.normcase(str(source_path.resolve()))
        == os.path.normcase(str(destination_path.resolve()))
    ):
        print("SKIPPED: File is already correctly named")
        continue

    if destination_path.exists():
        print("SKIPPED: Destination already exists")
        continue

    if DRY_RUN:
        print("DRY RUN: Would rename approved file")

    else:
        source_path.rename(
            destination_path
        )

        print("RENAMED")