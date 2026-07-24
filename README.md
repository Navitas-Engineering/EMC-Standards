# Standards PDF Catalogue Automation

A Python tool for analysing, validating, reporting, and safely renaming technical standards PDFs so they follow an existing standards-library naming convention.

> **Current stage:** Beta refinement and dry-run validation  
> **Recommended settings:** `DRY_RUN = True` and `EXPORT_RESULTS = True`

## 1. Folder layout

The application code and the target documents are intentionally kept separate at the same parent level:

```text
C:\Users\JoshuaDickens\Documents\
|
|-- Automation\
|   |-- Code\
|   |   |-- Script.py
|   |   |-- extraction.py
|   |   |-- extraction_continued.py
|   |   |-- filename_hint.py
|   |   |-- processing.py
|   |   |-- utils.py
|   |   |-- validate_standard.py
|   |   `-- README.md
|   |
|   `-- RenameResults.xlsx
|
`-- Target\
    |-- standard1.pdf
    |-- standard2.pdf
    `-- subfolders\
        `-- more-standards.pdf
```

In this arrangement:

- `Automation` contains the project and its reports;
- `Automation\Code` contains all Python source files;
- `Target` contains the PDFs to process;
- `Target` may contain subfolders because PDF discovery is recursive;
- `RenameResults.xlsx` is written inside `Automation`, not inside `Target`.

The script calculates these paths from the actual location of `Script.py`. It therefore does not depend on the current PowerShell working directory.

## 2. Project goals

The tool is intended to:

- find PDFs recursively within the target folder;
- extract text from the first pages using PyMuPDF;
- detect and score possible standard codes;
- normalise the selected code to the library convention;
- extract publication year, amendment, and amendment year;
- use the current filename as a supporting validation hint;
- create a proposed filename;
- flag uncertain or contradictory results for review;
- export all results to Excel;
- rename only results that pass validation.

The aim is not 100% automatic extraction. It is a reliable bulk-cataloguing assistant that automates straightforward files and exposes exceptions clearly.

## 3. Library naming convention

Examples:

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

Key rules:

- slashes normally become underscores;
- hyphens within standard numbers are preserved;
- multipart numeric identifiers retain their hyphens;
- `BS EN` becomes `EN`;
- amendments follow the publication year;
- interpretation sheets use `ISH` and their year.

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

## 4. Requirements

- Python 3
- pandas
- PyMuPDF
- openpyxl
- NumPy

Install dependencies with the same Python interpreter used to run the project:

```powershell
python -m pip install pandas pymupdf openpyxl numpy
```

For the current explicit interpreter location:

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" -m pip install pandas pymupdf openpyxl numpy
```

The Excel package is named `openpyxl`, ending with a lowercase letter `l`, not the number `1`.

## 5. Path configuration

At the top of `Script.py`, import `Path`:

```python
from pathlib import Path
```

Use the following configuration:

```python
DRY_RUN = True
EXPORT_RESULTS = True

TARGET_FOLDER_NAME = "Target"

# C:\Users\JoshuaDickens\Documents\Automation\Code
CODE_DIRECTORY = Path(__file__).resolve().parent

# C:\Users\JoshuaDickens\Documents\Automation
AUTOMATION_DIRECTORY = CODE_DIRECTORY.parent

# C:\Users\JoshuaDickens\Documents
DOCUMENTS_DIRECTORY = AUTOMATION_DIRECTORY.parent

# C:\Users\JoshuaDickens\Documents\Target
TARGET_DIRECTORY = (
    DOCUMENTS_DIRECTORY
    / TARGET_FOLDER_NAME
)

# C:\Users\JoshuaDickens\Documents\Automation\RenameResults.xlsx
RESULTS_WORKBOOK = (
    AUTOMATION_DIRECTORY
    / "RenameResults.xlsx"
)
```

The path is derived as follows:

```text
Script.py
-> Code
-> Automation
-> Documents
-> Target
```

To process a different sibling folder, change only:

```python
TARGET_FOLDER_NAME = "Another Target Folder"
```

The alternative folder must sit beside `Automation`, for example:

```text
Documents\
|-- Automation\
|-- Target\
`-- Another Target Folder\
```

### Validate the path

Before calling `get_file_names()`, validate and display the paths:

```python
print("Project locations:")
print(f"  Code directory:      {CODE_DIRECTORY}")
print(f"  Automation folder:   {AUTOMATION_DIRECTORY}")
print(f"  Documents folder:    {DOCUMENTS_DIRECTORY}")
print(f"  Target directory:    {TARGET_DIRECTORY}")
print(f"  Results workbook:    {RESULTS_WORKBOOK}")
print()

if not TARGET_DIRECTORY.exists():
    raise FileNotFoundError(
        "The target PDF directory could not be found:\n"
        f"{TARGET_DIRECTORY}"
    )

if not TARGET_DIRECTORY.is_dir():
    raise NotADirectoryError(
        "The configured target path is not a directory:\n"
        f"{TARGET_DIRECTORY}"
    )

sample_list = get_file_names(
    str(TARGET_DIRECTORY)
)
```

## 6. Configuration flags

### Recommended development settings

```python
DRY_RUN = True
EXPORT_RESULTS = True
```

This will:

- analyse all target PDFs;
- rename nothing;
- export the Excel review report.

### Real rename settings

```python
DRY_RUN = False
EXPORT_RESULTS = True
```

This will:

- rename only records with `status == "SUCCESS"`;
- leave `REVIEW_REQUIRED` and `NO_CANDIDATE` files untouched;
- export the outcome of every attempted operation.

Keep dry-run mode enabled until the report and a representative sample of successes have been checked.

## 7. Project modules

### `Script.py`

Main entry point. It resolves paths, discovers PDFs, processes every file, controls dry-run or real-rename behaviour, and exports the report.

### `extraction.py`

Extracts PDF text and detects candidate standard codes.

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

Normalises codes, extracts year and amendment details, builds filenames, and performs safe renames.

```python
normalise_code(code)
extract_designation_metadata(pages, raw_code)
build_filename(standard)
rename_file(old_path, standard)
```

### `filename_hint.py`

Extracts hints from the current filename and performs tolerant code comparison.

```python
extract_filename_hint(file_path)
normalise_hint_text(text)
filename_contains_code(filename_text, extracted_code)
```

Punctuation, spaces, underscores, slashes, and hyphens are removed before comparison. The extracted code must be contained in the cleaned current filename.

### `processing.py`

Runs the complete pipeline for one file:

```text
PDF
-> extract pages
-> extract filename hints
-> score candidates
-> select candidate
-> normalise code
-> extract metadata
-> validate metadata
-> build proposed filename
-> validate against current filename
-> return StandardData
```

Important functions:

```python
process_file(file_path)
test_single_file(file_path)
```

A `StandardData` result is returned even when no candidate is found, ensuring every PDF is represented in the report.

### `validate_standard.py`

Assigns a workflow status and reasons. Checks include missing years, suspicious BR years, low or zero extracted text, code disagreement, year disagreement, and amendment disagreement.

### `utils.py`

Contains `StandardData`, including:

```text
raw_code
normalised_code
year
amendment
amendment_year
filename
score
source_filename
filename_hint_code
filename_hint_year
filename_hint_amendment
filename_hint_amendment_year
status
reasons
extracted_text_length
proposed_path
rename_result
```

`reasons` remains a list internally. Use `reasons_text()` when displaying or exporting it.

## 8. Running the project

The script can be launched from any PowerShell working directory because its paths are relative to `Script.py`:

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\JoshuaDickens\Documents\Automation\Code\Script.py"
```

Expected resolved paths:

```text
Code directory:      C:\Users\JoshuaDickens\Documents\Automation\Code
Automation folder:   C:\Users\JoshuaDickens\Documents\Automation
Documents folder:    C:\Users\JoshuaDickens\Documents
Target directory:    C:\Users\JoshuaDickens\Documents\Target
Results workbook:    C:\Users\JoshuaDickens\Documents\Automation\RenameResults.xlsx
```

## 9. Status system

### `SUCCESS`

The proposed result passed current validation and is eligible for automatic renaming when `DRY_RUN = False`.

### `REVIEW_REQUIRED`

A proposed result exists, but at least one signal requires manual checking.

Typical reasons:

```text
Publication year differs from filename hint
Extracted code is not contained in current filename
Publication year requires manual review
Suspicious BR publication year
No extractable text
Very little extractable text; PDF may require manual review
Invalid amendment removed
```

### `NO_CANDIDATE`

No standard-code candidate was selected. The reasons and extracted-text length help distinguish image-only PDFs from text PDFs that do not match current patterns.

## 10. Filename hints

The current filename is supporting evidence, not the source of truth.

For example:

```text
Current filename: EN_12015_2004.pdf
Extracted result:  EN_12015_2015
```

Expected outcome:

```text
Status: REVIEW_REQUIRED
Reason: Publication year differs from filename hint (2004 vs 2015)
```

Neither value automatically overrides the other.

Containment comparison allows formatting variation such as:

```text
Extracted code: GE_RT_8270
Current filename: GE RT8270 issue 2.pdf
```

Both clean to compatible alphanumeric text, so this does not create an unnecessary code mismatch.

## 11. Excel report

With `EXPORT_RESULTS = True`, the workbook is saved to:

```text
C:\Users\JoshuaDickens\Documents\Automation\RenameResults.xlsx
```

It contains:

- `All Results` — every processed PDF;
- `Review Required` — every non-success record;
- `Summary` — counts by status.

Useful columns include:

```text
Original File
Source Filename
Filename Hint Code
Filename Hint Year
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
```

If Excel is holding the report open, Windows may raise:

```text
PermissionError: [Errno 13] Permission denied: 'RenameResults.xlsx'
```

Close the workbook in Excel and rerun the script. A timestamped fallback report may also be used:

```python
fallback_workbook = (
    AUTOMATION_DIRECTORY
    / f"RenameResults_{timestamp}.xlsx"
)
```

## 12. Rename safety

A file must be renamed only when:

```python
standard.status == "SUCCESS"
```

`rename_file()` additionally checks that:

- the source exists;
- the source is a PDF;
- a proposed filename exists;
- the destination does not already exist;
- the old and new paths are not identical.

An already correctly named file is treated as a successful no-op. Review and no-candidate files remain untouched.

## 13. Metadata extraction order

`extract_designation_metadata()` currently checks:

1. interpretation-sheet designations;
2. amendment designations;
3. explicitly labelled dates;
4. years near the selected standard code;
5. fallback years on early pages.

Examples:

```text
IEC 62271-1:2017/ISH1:2021
-> year=2017, amendment=ISH, amendment_year=2021

EN 55032:2015+A11:2020
-> year=2015, amendment=A11, amendment_year=2020
```

An amendment year earlier than the publication year is removed and recorded as a review reason.

## 14. Known limitations

### Wrong years from surrounding text

Years near terms such as `SUPERSEDES`, `WITHDRAWN`, `REPLACES`, and `REFERENCES` may be selected incorrectly. Filename comparison catches many such conflicts, but context-aware year extraction remains a development task.

### Image-only PDFs

PyMuPDF may return no text for scanned PDFs. These are retained in the review workflow with `No extractable text` in the reasons. OCR is not currently part of the automatic pipeline.

### Competing designations

A document may mention several standards. A draft, referenced, related, or superseded designation can occasionally win candidate scoring. Filename containment validation helps detect these outcomes.

### Filename hints can also be wrong

A mismatch does not prove the PDF extraction is wrong. It is a reason for manual review, not an automatic override.

## 15. Review workflow

1. Place target PDFs under `C:\Users\JoshuaDickens\Documents\Target`.
2. Set:

   ```python
   DRY_RUN = True
   EXPORT_RESULTS = True
   ```

3. Run `Script.py`.
4. Open `Automation\RenameResults.xlsx`.
5. Review the `Summary` sheet.
6. Sort or group `Review Required` by `Reasons`.
7. Investigate repeated failure classes rather than isolated files.
8. Spot-check a representative set of `SUCCESS` records.
9. Add only rules that are generally useful.
10. Rerun and compare status counts.
11. Back up the target folder before enabling real renaming.
12. Set `DRY_RUN = False` only when the report is acceptable.

## 16. Targeted debugging

Use paths based on `TARGET_DIRECTORY` rather than hard-coded relative paths:

```python
test_single_file(
    str(
        TARGET_DIRECTORY
        / "Documents"
        / "EN_12015_2004.pdf"
    )
)
```

This continues to work regardless of the current PowerShell directory.

`test_single_file()` prints candidate scores, the selected result, validation status, reasons, and additional page details for no-candidate files.

## 17. Recommended next tasks

1. Group current review records by reason.
2. Add bounded and context-aware year matching.
3. Reject or penalise years near:

   ```text
   SUPERSEDES
   SUPERSEDED
   WITHDRAWN
   REPLACES
   REPLACED
   REFERENCE
   REFERENCES
   ```

4. Keep OCR as a separate future stage.
5. Add automated regression tests for known code and filename examples.
6. Continue treating filenames as hints only.
7. Integrate reviewed results with `Library.xlsm` after rename reliability is established.

## 18. Current beta result

A recent validation run produced:

```text
SUCCESS            44
REVIEW_REQUIRED    16
NO_CANDIDATE        5
TOTAL               65
```

This is a useful beta-stage result: uncertain or contradictory files are being stopped for manual review instead of being silently renamed.

## 19. Safety reminders

- Keep `DRY_RUN = True` during development.
- Keep `EXPORT_RESULTS = True` so every run produces evidence.
- Review the workbook before any real rename.
- Rename only `SUCCESS` records.
- Keep a backup before bulk filesystem operations.
- Do not automatically trust either the filename or a plausible extraction when they disagree.
- Avoid overfitting to one unusual PDF unless the resulting rule is generally useful.
