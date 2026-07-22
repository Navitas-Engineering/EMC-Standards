from pathlib import Path
from extraction import extract_pages, is_junk_candidate, score_candidates, choose_best_candidate, get_file_names,  KNOWN_PREFIXES
import re
 
test_file= Path(__file__).resolve().parents[1] / "Sample Documents" / "DLR_ENG_STD_ES102_2012.pdf"

def test_contains_DLR():
    test_pages = extract_pages(test_file)
    
    test_scores = score_candidates(test_pages)
    print(f"Scores for {test_file}: {test_scores}")
    test_best_candidate = str(choose_best_candidate(test_scores))
    print(f"Best candidate for {test_file}: {test_best_candidate}")

    assert re.match(r"^(?=.*DLR)(?=.*ENG)(?=.*STD)(?=.*ES)(?=.*102).*$", test_best_candidate), f"Could not extract code, expected 'DLR_ENG_STD_ES102', but got '{test_best_candidate}'"
    
    
"""def test_equals_DLR():

    test_pages = extract_pages(test_file)
    test_scores = score_candidates(test_pages)
    print(f"Scores for {test_file}: {test_scores}")
    test_best_candidate = str(choose_best_candidate(test_scores))
    print(f"Best candidate for {test_file}: {test_best_candidate}")
    
    assert test_best_candidate == "DLR_ENG_STD_ES102_2012", f"Code reformatting failed, expected 'DLR_ENG_STD_ES102_2012', but got '{test_best_candidate}'"
"""
