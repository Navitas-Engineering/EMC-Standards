# Standards PDF Catalogue Automation

A Python tool for analysing, validating, and safely renaming technical standards PDFs so they follow an existing standards-library naming convention.

The project is designed for a collection of approximately 600 PDFs stored in a SharePoint-synchronised folder. It extracts standard designations and publication metadata from PDFs, compares the results with useful information in the current filenames, flags uncertain results for manual review, and can rename files that pass validation.

> **Current stage:** Beta refinement and dry-run validation
>
> **Recommended settings:** `DRY_RUN = True` and `EXPORT_RESULTS = True`

---

## Project goals

The tool is intended to:

- detect a standard code from the first pages of a PDF;
- normalise that code to the existing library format;
- extract publication year, amendment, and amendment year;
- use the current filename as a validation hint;
- create a proposed safe filename;
- separate successful results from files requiring review;
- export a review workbook;
- rename only files considered safe when dry-run mode is disabled.

The aim is not perfect automatic extraction. The aim is a reliable bulk-cataloguing assistant that processes straightforward files automatically and clearly identifies exceptions.

---

## Existing library naming convention

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

General rules:

- slashes are normally converted to underscores;
- hyphens inside standard numbers are preserved;
- multipart numeric standard numbers retain their hyphens;
- `BS EN` standards are stored under `EN`;
- amendments are appended after the publication year;
- interpretation-sheet suffixes use `ISH` followed by the interpretation-sheet year.

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

## Project structure

```text
.
|-- Script.py
|-- extraction.py
|-- extraction_continued.py
|-- filename_hint.py
|-- processing.py
|-- utils.py
|-- validate_standard.py
|-- Test Docs/
`-- RenameResults.xlsx          # generated report
```

### `Script.py`

Main entry point.

Responsibilities:

- reads all PDFs from the configured directory;
- calls `process_file()` for every PDF;
- prints proposed changes and validation results;
- protects review items from automatic renaming;
- exports the full results workbook;
- optionally performs real renames.

### `extraction.py`

Responsible for PDF text extraction and candidate detection.

Important functions:

```python
extract_pages(file_path)
find_candidates(page_text)
score_candidates(pages)
choose_best_candidate(scores)
get_file_names(directory)
is_junk_candidate(candidate)
```

PyMuPDF (`fitz`) reads the first few pages. Candidate regular expressions identify likely standards, which are then scored using page number, position, prefix, structure, and surrounding context.

### `extraction_continued.py`

Responsible for code normalisation, metadata extraction, filename construction, and physical renaming.

Important functions:

```python
normalise_code(code)
extract_designation_metadata(pages, raw_code)
build_filename(standard)
rename_file(old_path, standard)
```

### `filename_hint.py`

Extracts useful hints from the current filename.

The current filename is treated as supporting evidence, not as the source of truth. Code comparison is deliberately tolerant: punctuation, spaces, underscores, slashes, and hyphens are removed before a containment check is performed.

Examples that can match the same extracted code:

```text
GE_RT_8270_2007.pdf
GE RT8270 issue 2.pdf
Copy of GE-RT-8270.pdf
```

Important functions:

```python
extract_filename_hint(file_path)
normalise_hint_text(text)
filename_contains_code(filename_text, extracted_code)
```

### `processing.py`

Runs the complete pipeline for one PDF.

```text
PDF
-> extract pages
-> extract filename hint
-> score candidates
-> select best candidate
-> normalise code
-> extract metadata
-> validate metadata
-> build proposed filename
-> validate against filename hint
-> return StandardData
```

Important functions:

```python
process_file(file_path)
test_single_file(file_path)
```

`process_file()` returns a `StandardData` object even when no standard candidate is found. This ensures every PDF appears in the review report.

### `validate_standard.py`

Determines whether a proposed result is safe to rename automatically.

Validation checks include:

- missing or zero publication year;
- suspicious BR publication year;
- no or very little extractable text;
- extracted code not contained in the current filename;
- filename year and extracted year disagreement;
- amendment and amendment-year disagreement;
- invalid amendment metadata.

### `utils.py`

Contains the `StandardData` class used to pass information through the pipeline.

Its data includes:

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

`reasons` remains a Python list internally. Use `reasons_text()` when writing the reasons to the console or Excel.

---

## Requirements

- Python 3
- pandas
- PyMuPDF
- openpyxl
- NumPy

Install the dependencies using the same Python interpreter that runs the script:

```powershell
python -m pip install pandas pymupdf openpyxl numpy
```

If a specific Python installation is being used:

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" -m pip install pandas pymupdf openpyxl numpy
```

The Excel package is named `openpyxl`, ending with a lowercase letter `l`, not the number `1`.

---

## Configuration

At the top of `Script.py`:

```python
DRY_RUN = True
EXPORT_RESULTS = True

DIRECTORY = r"Test Docs"
RESULTS_WORKBOOK = "RenameResults.xlsx"
```

### Safe development configuration

```python
DRY_RUN = True
EXPORT_RESULTS = True
```

This configuration:

- processes all PDFs;
- renames nothing;
- exports a review workbook.

### Real rename configuration

```python
DRY_RUN = False
EXPORT_RESULTS = True
```

This configuration:

- renames only records with `status == "SUCCESS"`;
- leaves review and no-candidate files untouched;
- records all outcomes in the workbook.

Do not disable dry-run mode until the review workbook has been checked carefully.

---

## Running the tool

From PowerShell, change into the project directory and run:

```powershell
python Script.py
```

Or use the exact interpreter:

```powershell
& "C:\Users\JoshuaDickens\AppData\Local\Programs\Python\Python314\python.exe" Script.py
```

A typical status summary may look like:

```text
SUCCESS            44
REVIEW_REQUIRED    16
NO_CANDIDATE        5
```

These statuses are workflow decisions, not measures of whether the source PDF itself is valid.

---

## Status system

### `SUCCESS`

The extracted result passed the current validation rules and may be eligible for automatic renaming.

### `REVIEW_REQUIRED`

The system produced a result, but one or more signals require manual checking.

Typical reasons include:

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

No suitable standard-code candidate was detected.

The reason field distinguishes between PDFs with no extractable text and PDFs that contain text but do not match the current candidate patterns.

---

## Filename hints

Filename hints are used only for validation.

The extraction result remains the primary proposed result. A disagreement causes manual review rather than automatically substituting the filename value.

For example:

```text
Current filename: EN_12015_2004.pdf
Extracted result: EN_12015_2015
```

The file becomes:

```text
Status: REVIEW_REQUIRED
Reason: Publication year differs from filename hint (2004 vs 2015)
```

The tool does not automatically decide that either `2004` or `2015` is correct.

This protects against both incorrect PDF extraction and incorrectly named source files.

---

## Excel report

When `EXPORT_RESULTS = True`, the script creates an Excel workbook containing:

### `All Results`

Every processed PDF and its full extraction, validation, and rename information.

### `Review Required`

Every record whose status is not `SUCCESS`.

### `Summary`

A count of records by status.

Useful report columns include:

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
```

### Workbook locked by Excel

If export raises:

```text
PermissionError: [Errno 13] Permission denied: 'RenameResults.xlsx'
```

close `RenameResults.xlsx` in Excel and run the script again. Excel normally locks a workbook while it is open.

The script may also be configured to save a timestamped fallback file when the main workbook is locked.

---

## Rename safety

A real rename should occur only if:

```python
standard.status == "SUCCESS"
```

`rename_file()` also checks that:

- the source exists;
- the source is a PDF;
- a generated filename exists;
- the destination does not already exist;
- the source and destination are not the same path.

An already correctly named file is treated as a successful no-op.

Review items and no-candidate files must not be renamed automatically.

---

## Candidate scoring

Candidate scores currently consider:

- early-page weighting;
- position near the beginning of a page;
- known standard prefixes;
- numeric structure;
- slash and multipart structure;
- EN/IEC designation patterns;
- superseded or withdrawn context;
- committee-reference context;
- penalties for standalone `TS` candidates.

The standalone `TS` penalty helps ensure that an extracted candidate such as:

```text
IEC 61000-1-2
```

can beat a weaker partial candidate such as:

```text
TS 61000-1-2
```

Do not add arbitrary low-score validation thresholds until the score distribution from a representative full-library run has been reviewed.

---

## Metadata extraction priority

`extract_designation_metadata()` currently attempts metadata extraction in this order:

1. interpretation-sheet designation;
2. amendment designation;
3. explicitly labelled date;
4. standard-code-near-year match;
5. weighted fallback year from early pages.

Examples:

```text
IEC 62271-1:2017/ISH1:2021
-> year=2017, amendment=ISH, amendment_year=2021

EN 55032:2015+A11:2020
-> year=2015, amendment=A11, amendment_year=2020
```

If an amendment year is earlier than the publication year, the amendment is removed and the reason is recorded for review.

---

## Known limitations

### Wrong years from surrounding text

Some PDFs contain later or earlier years in text such as:

```text
Supersedes
Withdrawn
Replaces
References
Amendment history
```

This can cause incorrect year selection. Filename-year disagreement now catches many of these cases, but metadata extraction still needs further context filtering.

### Image-only PDFs

Some PDFs return no text through PyMuPDF. These files are placed in the review workflow with `No extractable text` in the reasons.

OCR is not currently part of the automatic pipeline.

### Competing designations

A PDF can mention several standards. In some cases a draft, referenced, superseded, or related designation can outscore the document's actual designation.

Filename containment validation helps detect these outcomes but does not resolve them automatically.

### Filename hints may also be wrong

A filename mismatch does not prove that PDF extraction is wrong. It only indicates that manual review is appropriate.

---

## Recommended review workflow

1. Run with:

   ```python
   DRY_RUN = True
   EXPORT_RESULTS = True
   ```

2. Open `RenameResults.xlsx`.
3. Review the `Summary` sheet.
4. In `Review Required`, group or sort by `Reasons`.
5. Investigate repeated failure types rather than individual files in isolation.
6. Add only generally useful extraction or validation rules.
7. Rerun and compare the status counts.
8. Spot-check a selection of `SUCCESS` records as well as all review records.
9. Enable real renaming only when the report is acceptable.
10. Keep a backup of the PDF library before bulk renaming.

---

## Targeted debugging

Use `test_single_file()` for known difficult PDFs:

```python
from processing import test_single_file


test_single_file(
    r"Test Docs\Documents\EN_12015_2004.pdf"
)
```

The function prints:

- candidate scores;
- the selected result;
- status;
- reasons;
- page text and candidates when no code is detected.

Useful test groups include:

- wrong-year cases;
- competing-code cases;
- no-candidate files with extracted text;
- image-only PDFs;
- amendment and interpretation-sheet files.

---

## Suggested next development tasks

1. Inspect the current `REVIEW_REQUIRED` records by reason.
2. Add bounded and context-aware year matching.
3. Reject or penalise years found near terms such as:

   ```text
   SUPERSEDES
   SUPERSEDED
   WITHDRAWN
   REPLACES
   REPLACED
   REFERENCE
   REFERENCES
   ```

4. Distinguish no-candidate files with text from files with no extracted text in reporting.
5. Add automated tests for known filename and metadata examples.
6. Continue using the current filename as supporting evidence only.
7. Consider OCR as a separate future processing stage rather than adding it to the main pipeline prematurely.
8. Integrate reviewed results with the existing `Library.xlsm` register after rename reliability is established.

---

## Suggested test cases

At minimum, preserve regression tests for:

```text
BS EN 55032:2015
-> EN_55032_2015

BS EN 55032:2015+A11:2020
-> EN_55032_2015_A11_2020

IEC 62271-1:2017/ISH1:2021
-> IEC_62271-1_2017_ISH_2021

GM/RC1500
-> GM_RC_1500

GE/RT8270
-> GE_RT_8270

NR/L2/ELP/27716/01
-> NR_L2_ELP_27716-01

DLR-ENG-STD-ES102
-> DLR_ENG_STD_ES102
```

Also preserve mismatch tests such as:

```text
Current filename: RT_E_C_50003_2003.pdf
Extracted code: RT_E_G_50003
Expected status: REVIEW_REQUIRED
```

```text
Current filename: EN_12015_2004.pdf
Extracted year: 2015
Expected status: REVIEW_REQUIRED
```

---

## Safety notes

- Keep `DRY_RUN = True` during development.
- Export and inspect the workbook before real renaming.
- Rename only `SUCCESS` records.
- Do not automatically trust the filename over the PDF.
- Do not automatically trust a plausible PDF extraction over a conflicting filename.
- Keep backups before any bulk filesystem operation.
- Avoid overfitting to a single unusual PDF unless the resulting rule is generally useful.

---

## Current project result

The current validation run produced:

```text
SUCCESS            44
REVIEW_REQUIRED    16
NO_CANDIDATE        5
TOTAL               65
```

This is a positive beta-stage result: uncertain or contradictory files are being stopped for review rather than silently renamed.
