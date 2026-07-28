import sys
from pathlib import Path


TESTS_DIRECTORY = Path(__file__).resolve().parent
AUTOMATION_DIRECTORY = TESTS_DIRECTORY.parent
CODE_DIRECTORY = AUTOMATION_DIRECTORY / "Code"

if str(CODE_DIRECTORY) not in sys.path:
    sys.path.insert(
        0,
        str(CODE_DIRECTORY)
    )