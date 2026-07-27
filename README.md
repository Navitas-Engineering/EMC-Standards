# Standards PDF Catalogue Automation

A Python tool for analysing, validating, reporting, and safely renaming technical standards PDFs so they follow an existing standards-library naming convention.

The project has two controlled stages:

1. **Automatic processing** with `Script.py`.
2. **Manual approval processing** with `Rename_Approval.py`.

> **Current stage:** Beta refinement and dry-run validation  
> **Recommended starting settings:** `DRY_RUN = True` in both scripts and `EXPORT_RESULTS = True` in `Script.py`.

---

## Contents

- [Folder structure](#folder-structure)
- [Project purpose](#project-purpose)
- [Requirements](#requirements)
- [Configuration and paths](#configuration-and-paths)
- [Project files](#project-files)
- [Automatic processing workflow](#automatic-processing-workflow)
- [Automatic statuses](#automatic-statuses)
- [Excel report](#excel-report)
- [Manual review columns](#manual-review-columns)
- [Manual decisions](#manual-decisions)
- [Manual approval workflow](#manual-approval-workflow)
- [Running the scripts](#running-the-scripts)
- [Rename safety](#rename-safety)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Recommended operating procedure](#recommended-operating-procedure)

---

## Folder structure

The code folder and target folder are kept separately beneath the same parent location:

```text
C:\Users\JoshuaDickens\Documents\
|
|-- Automation\
|   |-- Code\
|   |   |-- Script.py
|   |   |-- Rename_Approval.py
|   |   |-- extraction.py
|   |   |-- extraction_continued.py
|   |   |-- filename_hint.py
|   |   |-- processing.py
|   |   |-- utils.py
|   |   |-- validate_standard.py
|   |   `-- README.md
|   |
|   `-- RenameResults_YYYY-MM-DD.xlsx
|
`-- Target\
    |-- standard1.pdf
    |-- standard2.pdf
    `-- subfolders\
        `-- additional-standard.pdf
```

The target scan is recursive, so PDFs can be stored directly in `Target` or in its subfolders.

The paths are calculated from the location of each Python script. The program therefore does not depend on the folder from which PowerShell or Visual Studio Code was opened.

---

## Project purpose

The tool is designed to:

- discover all PDFs below a chosen target folder;
- extract text from the first pages using PyMuPDF;
- detect and score possible technical-standard codes;
- select and normalise the best candidate;
- extract the publication year, amendment, and amendment year;
- use the current filename as a supporting validation hint;
- build a proposed filename in the library convention;
- prevent uncertain results from being renamed automatically;
- export a formatted Excel review report;
- automatically rename validated `SUCCESS` records when enabled;
- allow manually reviewed exceptions to be renamed separately.

The aim is not perfect automation. The aim is a reliable bulk-cataloguing helper that automates straightforward files and clearly identifies exceptions.

---

## Library naming convention

Examples include:

```text
BR_13422_1978
DLR_ENG_STD_ES102_2012
EN_12015_2004
EN_50121-3-2_2015
EN_55032_2015
EN_55032_2015_A11_2020
IEC_61439-1_2021
IEC_62271-1_2017_ISH_2021
IEC_61000-4-7_2002_A1_2009
GEGN_8646_2017
GE_RT_8270_2007
GM_RC_1500_1994
NR_L2_ELP_27716-01_2023
RT_E_C_50001_2003
```

General rules:

- slashes normally become underscores;
- hyphens within multipart standard numbers are preserved;
- `BS EN` is stored as `EN`;
- publication year follows the normalised code;
- amendments follow the publication year;
- interpretation sheets use `ISH` followed by their year.

Examples:

```text
BS EN 55032:2015
-> EN_55032_2015

BS EN 55032:2015+A11:2020
-> EN_55032_2015_A11_2020

IEC 62271-1:2017/ISH1:2021
-> IEC_62271-1_2017_ISH_2021

GM/RC1500
-> GM_RC_1500_1994

NR/L2/ELP/27716/01
-> NR_L2_ELP_27716-01_2023
```

---

## Requirements

- Python 3
- pandas
- PyMuPDF
- openpyxl
- NumPy

Install the packages with the same Python interpreter that runs the scripts:

```powershell
python -m pip install pandas pymupdf openpyxl numpy
```

Using the current explicit interpreter path:

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" -m pip install pandas pymupdf openpyxl numpy
```

The Excel package is named `openpyxl`, ending with a lowercase letter `l`, not the number `1`.

---

## Configuration and paths

### Main script

The current `Script.py` configuration is:

```python
DRY_RUN = True
EXPORT_RESULTS = True

CODE_DIRECTORY = Path(__file__).resolve().parent
AUTOMATION_DIRECTORY = CODE_DIRECTORY.parent
DOCUMENTS_DIRECTORY = AUTOMATION_DIRECTORY.parent

TARGET_DIRECTORY = DOCUMENTS_DIRECTORY / "Target"

RESULTS_WORKBOOK = (
    AUTOMATION_DIRECTORY
    / f"RenameResults_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
)
```

This resolves to paths such as:

```text
Code directory:    C:\Users\JoshuaDickens\Documents\Automation\Code
Automation root:   C:\Users\JoshuaDickens\Documents\Automation
Target directory:  C:\Users\JoshuaDickens\Documents\Target
Results workbook:  C:\Users\JoshuaDickens\Documents\Automation\RenameResults_2026-07-27.xlsx
```

To process another sibling folder, change:

```python
TARGET_DIRECTORY = DOCUMENTS_DIRECTORY / "Target"
```

For example:

```python
TARGET_DIRECTORY = DOCUMENTS_DIRECTORY / "Standards To Sort"
```

The selected folder must exist beside `Automation`.

### Approval script

`Rename_Approval.py` uses the report for the current date:

```python
RESULTS_WORKBOOK = (
    AUTOMATION_DIRECTORY
    / f"RenameResults_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
)
```

This means the report should normally be reviewed and processed on the same date it was created.

If approvals are applied on a later date, manually set the required workbook name, for example:

```python
RESULTS_WORKBOOK = (
    AUTOMATION_DIRECTORY
    / "RenameResults_2026-07-27.xlsx"
)
```

Always check the workbook path printed or configured before applying real renames.

---

## Project files

### `Script.py`

The main application entry point.

It:

- resolves project and target paths;
- confirms that the target folder exists;
- gets all PDF paths recursively;
- processes each PDF;
- catches per-file processing exceptions;
- performs dry-run previews or automatic `SUCCESS` renames;
- builds the complete results table;
- writes a dated Excel report;
- formats the workbook with Excel tables, filters, colours, widths, and a manual-decision dropdown.

### `Rename_Approval.py`

The separate manual-approval renamer.

It:

- loads the dated `RenameResults_YYYY-MM-DD.xlsx` workbook;
- reads the `All Results` sheet;
- checks that required columns exist;
- selects only rows with `Manual Decision = APPROVE`;
- uses `Approved Filename` when supplied;
- otherwise uses `Generated Filename`;
- previews or applies approved renames;
- skips missing sources, non-PDF sources, identical paths, and existing destinations.

### `extraction.py`

Extracts PDF text, detects candidates, scores candidates, and discovers PDF files.

Important functions:

```python
extract_pages(file_path)
find_candidates(page_text)
score_candidates(pages)
choose_best_candidate(scores)
get_file_names(directory)
is_junk_candidate(candidate)
```

### `extraction_continued.py`

Normalises codes, extracts metadata, builds filenames, and performs automatic renames.

Important functions:

```python
normalise_code(code)
extract_designation_metadata(pages, raw_code)
build_filename(standard)
rename_file(old_path, standard)
```

### `filename_hint.py`

Extracts useful information from the current filename and supports tolerant filename comparison.

The current filename is a validation hint, not an automatic source of truth.

### `processing.py`

Runs the complete processing pipeline for one PDF:

```text
PDF
-> extract pages
-> extract filename hints
-> score candidates
-> select the best candidate
-> normalise the code
-> extract metadata
-> apply metadata checks
-> build the proposed filename
-> validate the result
-> return StandardData
```

Important functions:

```python
process_file(file_path)
test_single_file(file_path)
```

### `validate_standard.py`

Assigns an automatic workflow status and records the reasons for review.

### `utils.py`

Contains the `StandardData` class used to carry the extraction, validation, filename, path, status, and reason information through the pipeline.

---

## Automatic processing workflow

### Safe analysis mode

Use:

```python
DRY_RUN = True
EXPORT_RESULTS = True
```

This will:

- analyse the target PDFs;
- print proposed operations;
- rename no PDFs;
- export the dated Excel report.

### Automatic rename mode

Use:

```python
DRY_RUN = False
EXPORT_RESULTS = True
```

This will:

- automatically rename only rows whose automatic status is `SUCCESS`;
- leave `REVIEW_REQUIRED` and `NO_CANDIDATE` records untouched;
- export the outcome of every processed file.

Always run and inspect a dry run before enabling automatic renaming.

---

## Automatic statuses

### `SUCCESS`

The extracted result passed the current automatic validation checks.

When `Script.py` has `DRY_RUN = False`, these records are eligible for automatic renaming.

### `REVIEW_REQUIRED`

The application generated a proposed result, but one or more signals require human review.

Typical reasons include:

```text
Publication year differs from filename hint
Extracted code is not contained in current filename
Publication year requires manual review
Suspicious BR publication year
No extractable text
Very little extractable text; PDF may require manual review
Invalid amendment removed
Processing error
Target already exists
```

### `NO_CANDIDATE`

No suitable standard-code candidate was selected.

The `Reasons` and `Extracted Text Length` columns help distinguish between an image-only PDF and a text PDF that is not covered by the current candidate patterns.

---

## Excel report

`Script.py` creates a dated report in `Automation`:

```text
RenameResults_YYYY-MM-DD.xlsx
```

For example:

```text
RenameResults_2026-07-27.xlsx
```

### Workbook sheets

The workbook contains only:

```text
All Results
Summary
```

There is no separate `Review Required` sheet. Review records are filtered directly inside the `All Results` table, keeping one authoritative copy of every manual decision.

### `All Results`

The complete output is formatted as the Excel table:

```text
tblRenameResults
```

The table includes:

- built-in sorting and filtering;
- alternating row styling;
- a frozen header row;
- sensible column widths;
- wrapped long-text columns;
- green status cells for `SUCCESS`;
- orange status cells for `REVIEW_REQUIRED`;
- red status cells for `NO_CANDIDATE`;
- pale-yellow manual-review cells;
- an `APPROVE / REJECT / HOLD` dropdown.

To see only records requiring attention, filter the `Status` column to:

```text
REVIEW_REQUIRED
NO_CANDIDATE
```

### `Summary`

The summary is formatted as the Excel table:

```text
tblRenameSummary
```

It contains the count of records by automatic status.

### Report columns

The current report includes:

```text
Original File
Source Filename
Filename Hint Code
Filename Hint Year
Filename Hint Amendment
Filename Hint Amendment Year
Raw Code
Normalised Code
Extracted Year
Amendment
Amendment Year
Score
Extracted Text Length
Generated Filename
Proposed Path
Status
Reasons
Rename Result
Manual Decision
Approved Filename
Reviewer Notes
```

---

## Manual review columns

The following columns are created automatically in every report:

```text
Manual Decision
Approved Filename
Reviewer Notes
```

They are blank by default.

### `Manual Decision`

Contains an Excel dropdown with:

```text
APPROVE
REJECT
HOLD
```

The dropdown is applied to all result rows that exist when the report is created.

### `Approved Filename`

An optional manual override for `Generated Filename`.

Enter the filename with or without `.pdf`. `Rename_Approval.py` removes a trailing `.pdf` before constructing the destination path.

### `Reviewer Notes`

Free text explaining why a record was approved, rejected, corrected, or placed on hold.

---

## Manual decisions

### `APPROVE`

Allows `Rename_Approval.py` to process the row.

#### Approve the generated filename

```text
Manual Decision: APPROVE
Approved Filename: [blank]
Reviewer Notes: Checked cover; generated designation and year confirmed
```

The approval script uses `Generated Filename`.

#### Approve a corrected filename

```text
Manual Decision: APPROVE
Approved Filename: NR_SP_SIG_50006_2006
Reviewer Notes: Corrected designation manually confirmed from document cover
```

The approval script uses `Approved Filename` instead of `Generated Filename`.

### `REJECT`

Means the proposed result is wrong and must not be renamed by the approval script.

```text
Manual Decision: REJECT
Approved Filename: [blank]
Reviewer Notes: Referenced standard selected instead of document designation
```

Any value in `Approved Filename` is ignored when the decision is `REJECT`.

### `HOLD`

Means no final decision has been reached.

```text
Manual Decision: HOLD
Approved Filename: [blank]
Reviewer Notes: Needs confirmation from document owner
```

Any value in `Approved Filename` is ignored when the decision is `HOLD`.

### Blank

A blank decision means the record has not been manually approved. It is ignored by `Rename_Approval.py`.

### Decision summary

```text
APPROVE + blank Approved Filename
-> use Generated Filename

APPROVE + populated Approved Filename
-> use Approved Filename

REJECT
-> do not rename

HOLD
-> do not rename

Blank
-> do not rename
```

If a generated result is wrong but the correct filename is known, use `APPROVE` and enter the corrected value in `Approved Filename`.

---

## Manual approval workflow

1. Run `Script.py` with:

   ```python
   DRY_RUN = True
   EXPORT_RESULTS = True
   ```

2. Open the dated `RenameResults_YYYY-MM-DD.xlsx` workbook.
3. Use the filters in `All Results` to find `REVIEW_REQUIRED` and `NO_CANDIDATE` records.
4. Inspect each relevant PDF.
5. Complete `Manual Decision` using the dropdown.
6. If necessary, enter a corrected value in `Approved Filename`.
7. Add useful evidence or comments in `Reviewer Notes`.
8. Save and close the workbook.
9. Run `Rename_Approval.py` with:

   ```python
   DRY_RUN = True
   ```

10. Check every printed source and target path.
11. When satisfied, change `Rename_Approval.py` to:

    ```python
    DRY_RUN = False
    ```

12. Run it again to apply only approved renames.

### Important workbook warning

Rerunning `Script.py` on the same date can overwrite the existing dated workbook and remove manual entries.

Before rerunning the main script after review has started, either:

- make a backup copy of the workbook; or
- rename the reviewed workbook and update `RESULTS_WORKBOOK` in `Rename_Approval.py` to point to it.

Also close the workbook in Excel before either Python script needs to read or overwrite it.

---

## Running the scripts

### Main processor

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\JoshuaDickens\Documents\Automation\Code\Script.py"
```

### Manual approval renamer

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\JoshuaDickens\Documents\Automation\Code\Rename_Approval.py"
```

Both scripts should be run in dry-run mode before real filesystem changes are allowed.

---

## Rename safety

### Main script

An automatic rename requires:

```python
standard.status == "SUCCESS"
```

### Approval script

A manual rename requires:

```text
Manual Decision = APPROVE
```

The approval script also:

- requires a filename from either `Approved Filename` or `Generated Filename`;
- checks that the source exists;
- confirms that the source has a `.pdf` extension;
- skips a file already correctly named;
- skips an existing destination;
- supports its own dry-run mode.

Keep a backup of the target folder before any real bulk rename operation.

---

## Known limitations

### Filename comparison

Older filenames may use shortened, legacy, or descriptive designations. A filename mismatch is therefore a review signal, not proof that extraction is wrong.

### Wrong years from surrounding text

Years near terms such as the following may occasionally be selected incorrectly:

```text
SUPERSEDES
SUPERSEDED
WITHDRAWN
REPLACES
REPLACED
REFERENCE
REFERENCES
```

### Image-only PDFs

PyMuPDF may return no text for scanned or image-only documents. These remain in the manual-review workflow. OCR is not currently part of the automatic pipeline.

### Competing designations

A referenced, related, draft, or superseded standard can occasionally outscore the document's actual designation.

### Current-date report lookup

`Rename_Approval.py` currently calculates the report filename from today's date. A report created on an earlier date must be referenced manually if approval is performed later.

### Approval results are not written back

The current `Rename_Approval.py` prints whether it would rename, skipped, or renamed each approved file, but it does not write those outcomes back into the Excel workbook.

---

## Troubleshooting

### `PermissionError` when exporting the workbook

Example:

```text
PermissionError: [Errno 13] Permission denied: 'RenameResults_YYYY-MM-DD.xlsx'
```

The workbook is normally open in Excel. Close it and rerun the script.

If the main report is locked, `Script.py` attempts to create a timestamped fallback file:

```text
RenameResults_YY-MM-DD_HH-MM-SS.xlsx
```

### No matching distribution for `openpyxl`

Confirm the package spelling:

```text
openpyxl
```

The final character is a lowercase `l`, not the number `1`.

### Approval workbook not found

`Rename_Approval.py` expects:

```text
Automation\RenameResults_<today's YYYY-MM-DD>.xlsx
```

Check the date in the filename. If the report was generated on another day, set `RESULTS_WORKBOOK` explicitly to the correct file.

### No approved records found

Confirm that:

- decisions were entered on `All Results`;
- the workbook was saved;
- the workbook was closed before running the script;
- the selected values are `APPROVE`;
- `Rename_Approval.py` points to the workbook that was edited.

### Destination already exists

The renamer deliberately skips the row. Inspect the destination file and decide whether it is a duplicate, an earlier rename, or a naming conflict.

### Source file does not exist

The file may already have been renamed, moved, or deleted after the report was created. Generate a new report or correct the source path before trying again.

---

## Optional targeted debugging

`Script.py` retains commented calls to `test_single_file()` at the end of the file.

For the current path structure, prefer paths derived from `TARGET_DIRECTORY`, for example:

```python
test_single_file(
    str(
        TARGET_DIRECTORY
        / "Documents"
        / "EN_12015_2004.pdf"
    )
)
```

This avoids relying on the PowerShell working directory.

---

## Recommended operating procedure

1. Back up the target documents.
2. Keep `DRY_RUN = True` in both scripts.
3. Run `Script.py` with `EXPORT_RESULTS = True`.
4. Inspect the status summary.
5. Filter `All Results` to review exceptions.
6. Spot-check a representative group of automatic successes.
7. Complete the manual-decision columns.
8. Save and close the report.
9. Run `Rename_Approval.py` in dry-run mode.
10. Check all approved targets.
11. If required, run the main script with `DRY_RUN = False` to apply automatic `SUCCESS` renames.
12. Run the approval script with `DRY_RUN = False` to apply explicit manual approvals.
13. Retain the Excel report as an audit record.

---

## Safety reminders

- Use dry-run mode before every real rename batch.
- Review the dated workbook before changing files.
- Do not leave `APPROVE` selected unless the generated or corrected filename has been verified.
- Use `APPROVE` plus `Approved Filename` when applying a manual correction.
- Use `REJECT` for an incorrect proposal that must not be applied.
- Use `HOLD` when further investigation is required.
- Keep manual decisions blank by default.
- Do not automatically trust either the filename or extracted result when they disagree.
- Keep backups before bulk filesystem operations.
