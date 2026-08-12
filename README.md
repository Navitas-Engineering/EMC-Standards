# Standards PDF Catalogue Automation

A Python tool to analyse, validate, report on, and (optionally) safely rename technical-standards PDF files so they conform to a consistent library naming convention.

The project automates high-confidence bulk catalogue updates while keeping uncertain results in a controlled human-review workflow.

Status: Beta refinement and controlled testing

Recommended safe settings while evaluating the project:
- DRY_RUN = True in both Script.py and Rename_Approval.py
- EXPORT_RESULTS = True in Script.py

---

## Key features

- Recursive discovery of standards PDFs under a configurable target folder.
- Text extraction from the first pages (PyMuPDF) and candidate detection for standard designations.
- Candidate canonicalisation, scoring, and automatic normalisation into a library filename convention.
- Extraction of publication years, amendments, and amendment years.
- Dry-run safe automatic renaming of only high-confidence (`SUCCESS`) results.
- Per-run timestamped Excel reports with an interactive approval workflow for manual review.
- Controlled approval processor to `APPROVE`, `REJECT`, or `HOLD` documents and apply filesystem changes safely.
- Extensive safeguards to prevent accidental overwrites or operations outside the configured target directory.

---

## Quick start

1. Install dependencies (Python 3.10+ recommended):

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

2. Configure the target directory in `Script.py` and `Rename_Approval.py` (both must point to the same folder):

```python
TARGET_DIRECTORY = DOCUMENTS_DIRECTORY / "Target"
REJECTED_DIRECTORY = TARGET_DIRECTORY / "Rejected"
HOLD_DIRECTORY = TARGET_DIRECTORY / "Hold"
```

3. Run a safe analysis (no filesystem changes):

```powershell
python "Code/Script.py"
# ensure Script.py sets DRY_RUN = True
```

4. Review the generated workbook in `Automation/Reports/RenameResults_YYYY-MM-DD_HH-MM-SS.xlsx` and use `Rename_Approval.py` to apply manual decisions when ready.

---

## Workflow overview

Script.py performs:

1. PDF discovery (recursive, excluding the configured `Rejected` folder)
2. Text extraction from pages
3. Filename-hint extraction
4. Candidate detection and canonicalisation
5. Candidate scoring and best-candidate selection
6. Code normalisation and metadata extraction (year, amendment)
7. Automatic validation and `Status` assignment (`SUCCESS`, `REVIEW_REQUIRED`, `NO_CANDIDATE`)
8. Proposed filename generation and (dry-run) report export or real rename for `SUCCESS` rows

Rename_Approval.py performs:

- Selection of the newest timestamped report (or a specified override)
- Validation of the workbook and `All Results` table
- Processing of `APPROVE`, `REJECT`, and `HOLD` decisions
- Moving files into `Rejected` or `Hold`, or renaming/moving approved files back to the main target
- Writing approval outcomes into the same workbook and appending to the `Audit Log`

---

## Reports and manual review

Each processing run writes a timestamped Excel workbook to `Automation/Reports/` named:

```
RenameResults_YYYY-MM-DD_HH-MM-SS.xlsx
```

The workbook contains `All Results`, `Summary`, and `Audit Log` worksheets. `All Results` is stored in an Excel table named `tblRenameResults` and includes columns such as `Original File`, `Normalised Code`, `Generated Filename`, `Status`, `Reasons`, `Manual Decision`, `Approved Filename`, and `Final Path`.

Use the dropdown in `Manual Decision` (`APPROVE`, `REJECT`, `HOLD`) and `Rename_Approval.py` to apply your decisions in a controlled way.

---

## Library filename convention

Generated filenames follow a compact convention, examples:

```
EN_55032_2015
EN_55032_2015_A11_2020
IEC_62271-1_2017_ISH_2021
GEGN_8646_2017
```

General rules:
- Slashes become underscores; hyphens within multipart numbers are preserved.
- `BS EN` is stored as `EN`.
- Publication year follows the normalised code; amendments follow the year.
- Interpretation sheets use `ISH` followed by their year.

---

## Safety and limitations

- Automatic renaming only occurs when `standard.status == "SUCCESS"` and `DRY_RUN = False`.
- The approval processor validates source and destination paths, checks file existence, and refuses to overwrite existing files.
- The system does not attempt broad filesystem searches to locate missing files; a moved file that no longer matches `Original File` or `Final Path` may fail validation.
- OCR is not performed by default; image-only PDFs will be flagged in `Reasons` as requiring review.

Always back up the target folder before running real (non-dry-run) operations.

---

## Tests and CI

Run tests with pytest from the `Automation` directory:

```powershell
python -m pytest Tests -v
```

The repository includes a GitHub Actions workflow that installs dependencies, runs flake8, and executes pytest on pushes and pull requests.

---

## Contributing

Contributions, bug reports, and suggestions are welcome. Open an issue describing the change you propose and include sample PDFs or details where helpful.

---

If you want, I can further shorten the README, add badges (CI, Python version), or open a PR with this change—tell me which you'd prefer.