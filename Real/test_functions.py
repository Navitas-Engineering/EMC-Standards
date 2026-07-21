from functions import extract_pages, is_junk_candidate, score_candidates, choose_best_candidate, get_file_names,  KNOWN_PREFIXES
test_file = r"Sample Documents\DLR_ENG_STD_ES102_2012.pdf"


def test_extract_pages():
    test_file = r"Sample Documents\DLR_ENG_STD_ES102_2012.pdf"
    pages = extract_pages(test_file)
    assert len(pages) > 0, "No pages extracted from the PDF."

def test_score_candidates():
    test_file = r"Sample Documents\DLR_ENG_STD_ES102_2012.pdf"
    pages = extract_pages(test_file)
    scores = score_candidates(pages)
    assert isinstance(scores, dict), "Scores should be a dictionary."
    assert len(scores) > 0, "No candidates scored."

def test_choose_best_candidate():
    pages = extract_pages(test_file)
    scores = score_candidates(pages)
    best_candidate = choose_best_candidate(scores)
    assert best_candidate is not None, "No best candidate found."

def test_get_file_names():
    directory = r"Sample Documents"
    file_list = get_file_names(directory)
    assert isinstance(file_list, list), "File list should be a list."
    assert len(file_list) > 0, "No files found in the directory."
