# Standards PDF Catalogue Automation

A Python tool for analysing, validating, reporting, and safely renaming technical-standards PDFs so they follow a consistent library naming convention.

The project uses two controlled stages:

1. **Automatic processing** with `Script.py`.
2. **Manual review and approval processing** with `Rename_Approval.py`.

The system is designed to automate straightforward records while keeping uncertain results in a controlled human-review workflow. The current filename is treated as supporting evidence only; it never automatically overrides metadata extracted from the PDF.

> **Project stage:** Beta refinement and controlled testing  
> **Recommended development settings:** `DRY_RUN = True` in both scripts and `EXPORT_RESULTS = True` in `Script.py`.

---

## Contents

- [Project objectives](#project-objectives)
- [Folder structure](#folder-structure)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration and paths](#configuration-and-paths)
- [Project files](#project-files)
- [Library naming convention](#library-naming-convention)
- [Automatic processing workflow](#automatic-processing-workflow)
- [Candidate detection and normalisation](#candidate-detection-and-normalisation)
- [Automatic statuses](#automatic-statuses)
- [Excel review reports](#excel-review-reports)
- [Manual review workflow](#manual-review-workflow)
- [Approval behaviour](#approval-behaviour)
- [Repeated approval runs](#repeated-approval-runs)
- [Filesystem safety](#filesystem-safety)
- [Running the scripts](#running-the-scripts)
- [Automated tests](#automated-tests)
- [GitHub Actions](#github-actions)
- [Known limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)
- [Recommended operating procedure](#recommended-operating-procedure)
- [Future improvements](#future-improvements)

---

## Project objectives

The tool is designed to:

- discover PDFs recursively below a configurable designated folder;
- ignore PDFs already moved into the configured `Rejected` folder;
- continue scanning PDFs in `Hold` because they may still require clarification;
- extract text from the first pages of each PDF using PyMuPDF;
- detect and score possible technical-standard designations;
- normalise selected codes into the library naming convention;
- extract publication years, amendments, and amendment years;
- use the existing filename as a validation hint rather than a source of truth;
- automatically rename only results that pass the current validation rules;
- produce a unique, timestamped Excel report for every processing run;
- record who created each report and whether the run was a dry run;
- support manual `APPROVE`, `REJECT`, and `HOLD` decisions;
- write real approval outcomes back into the same workbook;
- retain previous reports as a permanent audit history;
- keep every filesystem-changing operation dry-run safe.

The aim is not perfect extraction from every PDF. The aim is a safe and explainable bulk-cataloguing process that automates high-confidence documents and exposes uncertain documents for review.

---

## Folder structure

A typical development layout is:

```text
Documents\
├── Automation\
│   ├── Code\
│   │   ├── Script.py
│   │   ├── Rename_Approval.py
│   │   ├── extraction.py
│   │   ├── extraction_continued.py
│   │   ├── filename_hint.py
│   │   ├── processing.py
│   │   ├── validate_standard.py
│   │   └── utils.py
│   │   
│   ├── Reports\
│   │   └── RenameResults_YYYY-MM-DD_HH-MM-SS.xlsx
│   ├── Tests\
│   │   ├── conftest.py
│   │   ├── test_extraction.py
│   │   ├── test_file_discovery.py
│   │   ├── test_normalisation.py
│   │   └── test_processing_integration.py
│   ├── README.md
│   └── requirements.txt
└── Target\
    ├── PDF files
    ├── Rejected\
    └── Hold\
```

`Target` is a testing placeholder. In deployment, both scripts must point to the same designated standards folder, for example:

```python
TARGET_DIRECTORY = DOCUMENTS_DIRECTORY / "Dropbox Standards"
```

Paths are derived relative to the script location using `pathlib`, so the program does not depend on the directory from which PowerShell or Visual Studio Code was opened.

### Special subfolder behaviour

- **`Rejected`** contains documents that should not be stored in the standards library, such as letters, research documents, unrelated publications, or other unsuitable material. It is excluded from future PDF discovery.
- **`Hold`** contains documents awaiting clarification. It remains included in future scans.

Only the specifically configured `Rejected` path is excluded. An unrelated folder with the same name elsewhere in the tree is not globally excluded.

---

## Requirements

- Python 3.10 or later
- pandas
- PyMuPDF
- openpyxl
- NumPy
- pytest
- flake8

The project is currently developed locally with Python 3.14 and tested in GitHub Actions with Python 3.10.

---

## Installation

A root-level `requirements.txt` is recommended:

```text
pandas
pymupdf
openpyxl
numpy
pytest
flake8
```

Install dependencies with the same Python interpreter that will run the scripts:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Using an explicit interpreter:

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" -m pip install -r requirements.txt
```

The Excel package is named `openpyxl`, ending with a lowercase letter `l`, not the number `1`.

---

## Configuration and paths

### Main processor

The main configuration in `Script.py` includes:

```python
DRY_RUN = True
EXPORT_RESULTS = True

RUN_STARTED_AT = datetime.now()
CURRENT_USER = getuser()

CODE_DIRECTORY = Path(__file__).resolve().parent
AUTOMATION_DIRECTORY = CODE_DIRECTORY.parent
DOCUMENTS_DIRECTORY = AUTOMATION_DIRECTORY.parent
REPORTS_DIRECTORY = AUTOMATION_DIRECTORY / "Reports"

TARGET_DIRECTORY = DOCUMENTS_DIRECTORY / "Target"
REJECTED_DIRECTORY = TARGET_DIRECTORY / "Rejected"

RESULTS_WORKBOOK = (
    REPORTS_DIRECTORY
    / (
        "RenameResults_"
        f"{RUN_STARTED_AT.strftime('%Y-%m-%d_%H-%M-%S')}"
        ".xlsx"
    )
)
```

`RUN_STARTED_AT` is captured once so the filename and report audit entry use one consistent timestamp.

`Script.py` creates `REPORTS_DIRECTORY` when required:

```python
REPORTS_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True
)
```

### Approval processor

`Rename_Approval.py` must use the same designated target folder:

```python
TARGET_DIRECTORY = DOCUMENTS_DIRECTORY / "Target"
REJECTED_DIRECTORY = TARGET_DIRECTORY / "Rejected"
HOLD_DIRECTORY = TARGET_DIRECTORY / "Hold"
REPORTS_DIRECTORY = AUTOMATION_DIRECTORY / "Reports"
```

The default workbook selection is:

```python
RESULTS_WORKBOOK_OVERRIDE = None
```

When the value is `None`, the approval script selects the report with the newest timestamp embedded in a filename matching:

```text
RenameResults_YYYY-MM-DD_HH-MM-SS.xlsx
```

To process a specific report, set an explicit override:

```python
RESULTS_WORKBOOK_OVERRIDE = (
    REPORTS_DIRECTORY
    / "RenameResults_2026-07-28_13-45-00.xlsx"
)
```

The selected workbook and selection reason are printed before processing begins.

### User identification

Both scripts obtain the current operating-system username automatically:

```python
from getpass import getuser

CURRENT_USER = getuser()
```

No manually maintained user-name setting is required.

---

## Project files

### `Script.py`

The main application entry point. It:

- resolves project paths;
- validates the configured target directory;
- creates the reports directory where necessary;
- recursively discovers eligible PDFs;
- excludes the configured `Rejected` folder;
- processes each PDF independently;
- catches per-file processing exceptions;
- previews or performs automatic `SUCCESS` renames;
- creates a timestamped Excel report;
- records the creator and dry-run state;
- formats the workbook with tables, filters, colours, widths, hyperlinks, and review controls.

### `Rename_Approval.py`

The controlled manual-decision processor. It:

- selects the newest timestamped report unless overridden;
- reads the `All Results` worksheet;
- validates required columns;
- processes `APPROVE`, `REJECT`, and `HOLD` decisions;
- follows `Final Path` for documents previously moved to `Hold`;
- moves approved held files out of `Hold` and back into the main target directory;
- moves rejected files into `Rejected`;
- writes real, non-dry-run outcomes into the same workbook;
- appends an approval-run entry to `Audit Log`;
- prevents already completed approvals or rejections from being repeated.

### `extraction.py`

Responsible for:

- extracting text from the first pages of a PDF;
- finding possible designation candidates;
- canonicalising equivalent candidate forms;
- scoring candidates;
- choosing the highest-scoring candidate;
- recursively discovering PDFs.

Important functions include:

```python
extract_pages(file_path)
find_candidates(page_text)
canonicalise_candidate(candidate)
score_candidates(pages)
choose_best_candidate(scores)
get_file_names(directory, rejected_directory=None)
```

### `extraction_continued.py`

Responsible for:

- normalising selected standard codes;
- extracting publication and amendment metadata;
- constructing generated filenames;
- performing automatic renames.

Important functions include:

```python
normalise_code(code)
extract_designation_metadata(pages, raw_code)
build_filename(metadata)
rename_file(old_path, standard)
```

### `filename_hint.py`

Extracts useful hints from the existing filename and supports tolerant comparison between the existing filename and the extracted designation.

The existing filename is never used to silently replace extracted metadata.

### `processing.py`

Runs the full processing pipeline for one PDF and returns a `StandardData` object even when no candidate is found.

Important functions:

```python
process_file(file_path)
test_single_file(file_path)
```

### `validate_standard.py`

Applies validation rules, assigns the automatic status, and records human-readable review reasons.

### `utils.py`

Contains the `StandardData` class used to pass extraction, filename, validation, path, status, and reason information through the pipeline.

### `Tests`

Contains synthetic unit tests and real-PDF integration tests for:

- GEGN and GLGN candidate canonicalisation;
- code normalisation;
- filename construction;
- protection of existing code formats;
- `Rejected` exclusion;
- continued `Hold` discovery;
- real DLR document processing.

---

## Library naming convention

Examples include:

```text
BR_13422_1978
DLR_ENG_STD_ES102_2012
EN_12015_2004
EN_50121-3-2_2015
EN_55032_2015_A11_2020
IEC_61439-1_2021
IEC_62271-1_2017_ISH_2021
IEC_61000-4-7_2002_A1_2009
GEGN_8646_2017
GLGN_1620_2024
GE_RT_8270_2007
GM_RC_1500_1994
NR_L2_ELP_27716-01_2023
RT_E_C_50001_2003
```

General rules:

- slashes normally become underscores;
- hyphens within multipart standard numbers are preserved;
- `BS EN` is stored as `EN`;
- the publication year follows the normalised code;
- amendments follow the publication year;
- interpretation sheets use `ISH` followed by their year;
- `GEGN` and `GLGN` remain single prefix blocks.

Examples:

```text
BS EN 55032:2015
-> EN_55032_2015

BS EN 55032:2015+A11:2020
-> EN_55032_2015_A11_2020

IEC 62271-1:2017/ISH1:2021
-> IEC_62271-1_2017_ISH_2021

GE/GN/8646
-> GEGN_8646

GL/GN/1620
-> GLGN_1620

GE/RT/8270
-> GE_RT_8270

NR/L2/ELP/27716/01
-> NR_L2_ELP_27716-01
```

---

## Automatic processing workflow

`Script.py` follows this sequence:

```text
PDF discovery
-> text extraction
-> filename-hint extraction
-> candidate detection
-> candidate canonicalisation
-> candidate scoring
-> best-candidate selection
-> code normalisation
-> year and amendment extraction
-> validation
-> status assignment
-> proposed filename
-> dry-run preview or automatic SUCCESS rename
-> timestamped Excel report
```

### Safe analysis mode

Use:

```python
DRY_RUN = True
EXPORT_RESULTS = True
```

This mode:

- analyses eligible PDFs;
- prints proposed operations;
- makes no filesystem changes;
- creates a timestamped report;
- records that the processing run was a dry run.

### Automatic rename mode

Use:

```python
DRY_RUN = False
EXPORT_RESULTS = True
```

This mode:

- automatically renames only `SUCCESS` results;
- leaves `REVIEW_REQUIRED` and `NO_CANDIDATE` files untouched;
- records every result in the workbook.

Always inspect a dry run before enabling real automatic changes.

---

## Candidate detection and normalisation

### Candidate scoring

Candidate scores are influenced by:

- the page on which the candidate appears;
- position near the beginning of a page;
- recognised prefixes;
- multipart-number structure;
- occurrences across extracted pages;
- nearby negative context such as `SUPERSEDE`, `WITHDRAWN`, or `COMMITTEE REF`.

The system deliberately avoids document-specific rules where possible.

### GEGN and GLGN handling

Equivalent guidance-note forms are canonicalised before scoring:

```text
GEGN8646
GEGN 8646
GE/GN/8646
GE_GN_8646
GE-GN-8646
GE GN 8646
```

become:

```text
GEGN 8646
```

Equivalent `GLGN` forms are treated in the same way.

This allows equivalent occurrences to reinforce one candidate instead of splitting their scores across differently formatted strings. No separate GEGN/GLGN scoring bonus is currently applied.

Other codes remain unaffected. For example:

```text
GE/RT/8270
-> GE_RT_8270
```

---

## Automatic statuses

### `SUCCESS`

The extracted result passed the current automatic validation checks.

When `Script.py` has `DRY_RUN = False`, only these rows are eligible for automatic renaming.

### `REVIEW_REQUIRED`

A proposed result was generated, but one or more signals require human review.

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

`Reasons` and `Extracted Text Length` help distinguish image-only PDFs from text PDFs not covered by the current candidate patterns.

OCR is not a separate status. OCR-related problems are recorded in `Reasons`.

---

## Excel review reports

Every `Script.py` run creates a unique workbook in:

```text
Automation\Reports\
```

Naming format:

```text
RenameResults_YYYY-MM-DD_HH-MM-SS.xlsx
```

Example:

```text
RenameResults_2026-07-28_14-22-31.xlsx
```

A new run does not overwrite an earlier report or its manual decisions.

### Worksheets

The workbook contains:

```text
All Results
Summary
Audit Log
```

### `All Results`

The main data is stored in an Excel table named:

```text
tblRenameResults
```

It includes:

- sorting and filtering;
- a frozen header row;
- alternating row styling;
- wrapped long-text columns;
- green status cells for `SUCCESS`;
- orange status cells for `REVIEW_REQUIRED`;
- red status cells for `NO_CANDIDATE`;
- pale-yellow manual-review columns;
- an `APPROVE / REJECT / HOLD` dropdown;
- an `Open File` hyperlink using a relative path where possible.

The heading must be exactly:

```text
Open File
```

in both normal and exception result dictionaries.

There is no separate `Review Required` worksheet. Filter `Status` in `tblRenameResults` to find review records.

### Main report columns

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
Approval Result
Approved By
Approved At
Final Path
Open File
```

### `Summary`

Contains the automatic-status counts and is formatted as:

```text
tblRenameSummary
```

### `Audit Log`

Records processing and real approval runs. Typical fields are:

```text
Timestamp
Event
User
Dry Run
Script
Details
```

The initial `PROCESSING_RUN` entry records:

- when the workbook was created;
- the operating-system username;
- whether the processing run was a dry run;
- the target directory;
- processed-file and status counts.

A real approval run appends an `APPROVAL_RUN` entry. Approval dry runs do not modify the workbook.

---

## Manual review workflow

Manual-review columns are created automatically:

```text
Manual Decision
Approved Filename
Reviewer Notes
```

Approval-audit columns are also included:

```text
Approval Result
Approved By
Approved At
Final Path
```

### `Manual Decision`

Valid values are:

```text
APPROVE
REJECT
HOLD
```

Blank means no instruction.

### `Approved Filename`

Optional override for `Generated Filename`.

It may be entered with or without `.pdf`. A trailing `.pdf` is removed before the destination is constructed, and path components are discarded so that only a filename can be supplied.

### `Reviewer Notes`

Free text for review evidence, corrections, or clarification requirements.

---

## Approval behaviour

### `APPROVE` with blank `Approved Filename`

Uses `Generated Filename`.

### `APPROVE` with populated `Approved Filename`

Uses `Approved Filename` instead of the generated value.

### `REJECT`

Moves the original PDF into:

```text
<Target>\Rejected\
```

The original filename is retained. Existing destinations are never overwritten.

### `HOLD`

Moves the original PDF into:

```text
<Target>\Hold\
```

The original filename is retained. Hold is temporary and remains eligible for future review.

### Approving a previously held file

The row's `Final Path` is used to locate the document in `Hold`. The file is then renamed and moved out of `Hold` into the main target directory:

```text
<Target>\Hold\unclear-document.pdf
-> <Target>\EN_55032_2015.pdf
```

### Rejecting a previously held file

A held document later changed to `REJECT` is moved from `Hold` into `Rejected`.

### Blank

The file is left untouched and reconsidered on later approval runs.

---

## Repeated approval runs

The workbook is designed to be reused.

- blank rows remain available for later decisions;
- `HOLD` rows remain available for later clarification;
- failed real operations remain eligible for retry;
- completed approvals and rejections are skipped on later runs;
- `Final Path` is preferred over `Original File` when locating a previously moved held file.

A completed result is identified by an `Approval Result` beginning with:

```text
COMPLETED -
```

Changing the dropdown on a completed row does not automatically reverse the previous filesystem action. Completed approvals and rejections remain skipped. Reversal of a completed action must be handled deliberately outside this workflow.

If an approved file is later moved elsewhere as part of the normal library process, later approval loops still skip the completed row; the stored `Final Path` is the path produced at the time of approval, not permanent live tracking.

A held file moved manually away from both `Final Path` and `Original File` cannot be safely located automatically and will fail validation rather than causing a filesystem-wide filename search.

---

## Filesystem safety

### Main processor

Automatic renaming requires:

```python
standard.status == "SUCCESS"
```

### Approval processor

Before a rename or move, the script checks that:

- the source exists;
- the source is a file;
- the source has a `.pdf` extension;
- the source is inside the configured target directory;
- source and destination are not identical;
- the destination does not already exist.

Additional safeguards include:

- separate dry-run settings in both scripts;
- no overwrite of existing PDFs;
- explicit target-path validation;
- workbook lock checks before a real approval run;
- no workbook changes during approval dry runs;
- completed operations are not repeated;
- rejected and held files retain their original names when moved;
- approved held files are moved back to the main target only after an explicit approval.

Keep a backup before every real bulk operation.

---

## Running the scripts

Run commands from the project root rather than the Visual Studio Code installation directory.

```powershell
cd "C:\Users\JoshuaDickens\Documents\Automation"
```

### Main processor

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\JoshuaDickens\Documents\Automation\Code\Script.py"
```

### Manual approval processor

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\JoshuaDickens\Documents\Automation\Code\Rename_Approval.py"
```

Both scripts should be run in dry-run mode before real filesystem changes are enabled.

---

## Automated tests

The test suite uses pytest.

Current coverage includes:

- candidate canonicalisation for GEGN and GLGN variants;
- protection of unrelated formats such as `GE/RT/8270`;
- code normalisation and filename construction;
- candidate scoring and selection;
- PDF discovery;
- exclusion of the configured `Rejected` folder;
- continued discovery inside `Hold`;
- a real DLR processing integration test.

### Run all tests

From the `Automation` directory:

```powershell
python -m pytest Tests -v
```

Using the explicit interpreter:

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" -m pytest Tests -v
```

### Collect tests without running them

```powershell
python -m pytest Tests --collect-only -v
```

### Run one test file

```powershell
python -m pytest Tests\test_normalisation.py -v
```

### Important working-directory note

If pytest reports:

```text
collected 0 items
```

check the displayed `rootdir`. It should point to the Automation project, not:

```text
C:\Users\JoshuaDickens\AppData\Local\Programs\Microsoft VS Code
```

### Linting

Run the critical checks locally with:

```powershell
python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

Run the broader warning report with:

```powershell
python -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

---

## GitHub Actions

The repository includes a workflow that:

1. checks out the repository;
2. installs the configured Python version;
3. installs dependencies;
4. runs flake8;
5. runs pytest.

Example workflow:

```yaml
name: Python application

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"
          cache: "pip"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt

      - name: Lint for syntax errors and undefined names
        run: |
          python -m flake8 . \
            --count \
            --select=E9,F63,F7,F82 \
            --show-source \
            --statistics

      - name: Report other lint warnings
        run: |
          python -m flake8 . \
            --count \
            --exit-zero \
            --max-complexity=10 \
            --max-line-length=127 \
            --statistics

      - name: Run tests
        run: |
          python -m pytest Tests -v
```

GitHub Actions uses Ubuntu, so file and directory casing matters. `Tests`, `Code`, and module filenames must match the committed names exactly.

Real-PDF integration tests run in CI only if the permitted sample PDFs are committed at the paths expected by the tests. Missing optional samples may be skipped where the tests explicitly use `pytest.skip()`.

---

## Known limitations

### Filename comparison

Older filenames may contain shortened, legacy, or descriptive standard codes. A mismatch is a review signal, not proof that extraction is wrong.

The existing comparison is deliberately conservative and has not been expanded to override extracted metadata.

### Competing designations

Referenced, related, superseded, or replacement standards can occasionally outscore the document's actual designation.

### Year extraction

Year extraction can still select years associated with:

```text
SUPERSEDES
SUPERSEDED
WITHDRAWN
REPLACES
REPLACED
REFERENCE
REFERENCES
```

Some metadata expressions currently search broad text ranges. Bounded-context year extraction remains a future improvement.

### Image-only PDFs

PyMuPDF may return no text for scanned or image-only PDFs. These remain in manual review. OCR is not currently part of the automatic pipeline.

### Duplicate destinations

Renames and moves are skipped when the destination already exists. Existing files are never overwritten automatically.

### Duplicate candidate matches

A specific GEGN/GLGN pattern and a generic candidate pattern may detect the same occurrence. Canonicalisation unifies representation, but exact score values should not be treated as stable external interfaces.

### Completed decisions are not reversible through the dropdown

A completed approval or rejection is not automatically undone if `Manual Decision` is later changed. This prevents the review workbook from acting as an unrestricted undo mechanism.

### External file movement

After a completed approved file leaves the target as part of the downstream library workflow, the workbook does not track its new location. The completed audit remains valid, and later approval runs skip the row.

### Library workbook integration

Direct integration with `Library.xlsm` is intentionally out of scope. Approved files currently enter the existing library registration workflow separately.

---

## Troubleshooting

### No tests ran

Confirm the current directory:

```powershell
Get-Location
```

Then navigate to the project:

```powershell
cd "C:\Users\JoshuaDickens\Documents\Automation"
python -m pytest Tests -v
```

### Import errors during tests

Confirm `Tests\conftest.py` adds the `Code` directory to `sys.path`:

```python
import sys
from pathlib import Path

TESTS_DIRECTORY = Path(__file__).resolve().parent
AUTOMATION_DIRECTORY = TESTS_DIRECTORY.parent
CODE_DIRECTORY = AUTOMATION_DIRECTORY / "Code"

if str(CODE_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(CODE_DIRECTORY))
```

### Approval workbook not found

Check:

- the report exists in `Automation\Reports`;
- its name exactly matches the timestamped pattern;
- it is not an Excel temporary file beginning with `~$`;
- `RESULTS_WORKBOOK_OVERRIDE` is either `None` or a valid explicit path.

### Permission error when updating a report

Close the workbook in Excel before running real approval processing.

The approval script should check write access before changing PDFs, but the workbook must remain closed until processing finishes.

### Destination already exists

The operation is intentionally skipped. Inspect both files and decide whether the destination is a duplicate, a previous rename, or a naming conflict.

### Source file does not exist

The file may already have been moved, renamed, or deleted. For held files, confirm that `Final Path` points to the current location.

### Relative Open File link unavailable

Relative links may be unavailable when the workbook and PDF are on different Windows drives. The report records this rather than generating an invalid relative link.

### Incorrect target folder

Ensure both `Script.py` and `Rename_Approval.py` use the same designated folder. `Target` is only a testing placeholder.

---

## Recommended operating procedure

1. Back up the target documents.
2. Confirm both scripts point to the same designated target folder.
3. Keep `DRY_RUN = True` in both scripts.
4. Run `Script.py` with `EXPORT_RESULTS = True`.
5. Confirm `Rejected` files were excluded and `Hold` files remained visible.
6. Inspect the status summary and `Audit Log`.
7. Filter `All Results` to `REVIEW_REQUIRED` and `NO_CANDIDATE`.
8. Spot-check a representative sample of `SUCCESS` results.
9. Complete `Manual Decision`, `Approved Filename`, and `Reviewer Notes` where required.
10. Save and close the workbook.
11. Run `Rename_Approval.py` with `DRY_RUN = True`.
12. Check the selected workbook and every printed source and destination.
13. Set `DRY_RUN = False` only when satisfied.
14. Run the approval script again to apply decisions and write outcomes back.
15. Review `Approval Result`, `Final Path`, and `Audit Log`.
16. Move completed approved files into the downstream library-registration workflow.
17. Retain timestamped reports as audit records.

---

## Future improvements

Potential future work includes:

- improve year extraction using bounded context around the selected designation;
- deduplicate identical candidate occurrences produced by overlapping patterns;
- add unit tests for approval state transitions and workbook write-back;
- add tests for dry-run safety across every filesystem helper;
- preserve a detailed row-level history of repeated failed attempts if required;
- centralise shared target configuration in a small configuration module;
- improve candidate context without overfitting rules to individual PDFs;
- expand the permitted real-PDF regression sample set;
- evaluate OCR as a separate optional preprocessing stage;
- consider downstream library integration only after the current workflow is stable.

---

## Safety reminders

- Use dry-run mode before every real batch.
- Keep backups before bulk filesystem operations.
- Review the timestamped report before approving changes.
- Never automatically trust either the existing filename or extracted result when they disagree.
- Use `APPROVE` plus `Approved Filename` for a verified manual correction.
- Use `REJECT` only for documents that should leave the standards-library workflow.
- Use `HOLD` while clarification is still required.
- Leave undecided records blank.
- Close the workbook before real approval processing.
- Do not expect changing a completed row's dropdown to reverse the completed action.
- Keep deployment paths consistent between both scripts.
