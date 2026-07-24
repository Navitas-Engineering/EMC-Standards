# Real/test_functions.py
from pathlib import Path
from extraction import extract_pages, score_candidates, choose_best_candidate, get_file_names

root = Path(__file__).resolve().parents[1]
test_file = root / "Sample Documents" / "DLR_ENG_STD_ES102_2012.pdf"
test_dir = root / "Sample Documents"

def test_extract_pages():
    pages = extract_pages(str(test_file))
    assert len(pages) > 0

def test_score_candidates():
    pages = extract_pages(str(test_file))
    scores = score_candidates(pages)
    assert isinstance(scores, dict)
    assert len(scores) > 0

def test_choose_best_candidate():
    pages = extract_pages(str(test_file))
    scores = score_candidates(pages)
    best_candidate = choose_best_candidate(scores)
    assert best_candidate is not None

def test_get_file_names():
    file_list = get_file_names(str(test_dir))
    assert isinstance(file_list, list)
    assert len(file_list) > 0