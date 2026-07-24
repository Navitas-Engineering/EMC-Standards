from pathlib import Path
from processing import process_file
import re
 
test_file = (
    Path(__file__).resolve().parent.parent
    / "Standards"
    / "Sample Documents"
    / "DLR_ENG_STD_ES102_2012.pdf"
)
def test_contains_DLR():
    standard = process_file(test_file)

    assert re.match(r"^(?=.*DLR)(?=.*ENG)(?=.*STD)(?=.*ES)(?=.*102).*$", standard.filename), f"Could not extract code, expected 'DLR_ENG_STD_ES102', but got '{standard.filename}'"


def test_equals_DLR():  

    standard = process_file(test_file)

    assert standard.filename == "DLR_ENG_STD_ES102_2012"