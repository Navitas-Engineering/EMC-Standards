from extraction import choose_best_candidate, extract_pages, find_candidates, find_candidates, score_candidates
from extraction_continued import build_filename, extract_designation_metadata, normalise_code

def process_file(file_path):

    pages = extract_pages(file_path)

    scores = score_candidates(pages)

    standard = choose_best_candidate(scores)

    if standard is None:
        return None

    standard.normalised_code = normalise_code(
        standard.raw_code
    )

    metadata = extract_designation_metadata(
        pages,
        standard.raw_code
    )

    standard.year = metadata["year"]
    standard.amendment = metadata["amendment"]
    standard.amendment_year = metadata["amendment_year"]

    # BR documents should not have modern years
    if (
        standard.normalised_code.startswith("BR_")
        and standard.year is not None
        and standard.year > 2000
    ):
        standard.year = 0

    standard.filename = build_filename(
        standard
    )

    return standard

def test_single_file(file_path):
    """Test the extraction and scoring of a single PDF file.
    
    Args:
        file_path (str): The path to the PDF file to test.
    """
    print(f"Testing file: {file_path}")
    pages = extract_pages(file_path)
    scores = score_candidates(pages)
    print(f"Scores for {file_path}: {scores}")
    best_candidate = choose_best_candidate(scores)
    if best_candidate is not None:
        print(f"Best candidate for {file_path}: {best_candidate}")
    else:
        print(f"No valid candidate found for {file_path}")
        print("Dumping page texts for debugging:")
        for i, page in enumerate(pages):
            print(f"Page number: {page['page']}")
            print(f"Page {i+1}: {page['text']}")

        for page_data in pages:

            page_no = page_data["page"]

            candidates = find_candidates(
                page_data["text"]
            )

            print(f"\nPage {page_no}")

            for candidate in candidates:
              print(candidate)
