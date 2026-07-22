import fitz
import re
import os
from collections import defaultdict
import numpy as np

from utils import StandardData

MAX_PAGES = 5

KNOWN_PREFIXES = {
    "EN",
    "IEC",
    "NR",
    "RT",
    "GE",
    "GM",
    "DLR",
    "BR",
    "GEGN",
    "BS",
    "S",
    "EVS", 
}
"""Whitelist of known prefixes for document codes."""

def is_junk_candidate(candidate):
    """Determine if a candidate string is invalid based on known junk patterns.
    
    Args:
        candidate (str): The candidate string to evaluate.

    Returns:
        bool: True if the candidate is junk, False otherwise.
    """

    candidate = candidate.upper()

    banned = [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
        "ISS",
        "ISSUE",
        "DATE",
        "PAGE",
        "OF ",
        "CONTENTS",
        "APPENDIX",
        "SECTION",
        "FIGURE",
        "TABLE"
    ]

    return any(
        candidate.startswith(x)
        for x in banned
    )


def extract_pages(file_path):
    """Extract text from the first few pages of a PDF file.
    
    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list: A list of dictionaries containing page numbers and extracted text.
    """
    
    doc = fitz.open(file_path)
    pages = []
    
    pages_to_read = min(len(doc), MAX_PAGES)

    for page_num in range(pages_to_read):
        text = doc[page_num].get_text()
        pages.append({"page": page_num + 1, "text": text})
        
    return pages


def find_candidates(page_text):
    """Find potential document code candidates in the given page text.
    
    Args:
        page_text (str): The text extracted from a PDF page.
        
    Returns:
        list: A list of candidate strings that match known patterns."""

    patterns = [

        r'\bGEGN\d+\b',

        r'\bBR\s+\d+\b',

        r'NR(?:/[A-Z0-9]+){2,5}/\d+(?:-\d+)?',

        r'RT(?:/[A-Z0-9]+){2,5}/\d+(?:-\d+)?',

        r'[A-Z]{2,}(?:[-/][A-Z0-9]+){2,}',

        r'(?:BS\s+)?EN\s+\d+(?:-\d+)*',

        r'IEC\s+\d+(?:-\d+)*',

        r'GM/[A-Z]+\d+',

        r'\b[A-Z]{2,5}\s+\d{3,}\b'    ]

    candidates = []

    for pattern in patterns:

        for match in re.finditer(
            pattern,
            page_text,
            re.IGNORECASE
        ):

            candidates.append(
                (
                    match.group(),
                    match.start()
                )
            )
        

    return candidates

def score_candidates(pages):
    """Score candidate strings based on their occurrence and characteristics in the extracted pages.
    
    Args:
        pages (list): A list of dictionaries containing page numbers and extracted text.
    Returns:
            dict: A dictionary mapping candidate strings to their scores.
    """

    scores = defaultdict(int)

    page_weights = {
        1: 500,
        2: 100,
        3: 25,
        4: 10,
        5: 1
    }

    for page_data in pages:

        page_no = page_data["page"]

        candidates = find_candidates(
            page_data["text"]
        )

        for candidate, position in candidates:
            candidate = candidate.strip().upper()

            if is_junk_candidate(candidate):
                continue
            
            score = 0

            # Appears on early page
            score += page_weights.get(
                page_no,
                1
            )

            # Appears near start of page
            if position < 100:
                score += 500

            elif position < 250:
                score += 300

            elif position < 500:
                score += 150

            elif position < 1000:
                score += 50

            if "/" in candidate:
                score += 10

            if re.search(
                r'\d{3,}',
                candidate
            ):
                score += 10

            #context around candidate
            text = page_data["text"]

            window_start = max(0, position - 50)
            window_end = min(len(text), position + len(candidate) + 50)
            context = text[window_start:window_end].upper()

            if "SUPERSEDE" in context or "WITHDRAWN" in context:
                score -=300

            for prefix in KNOWN_PREFIXES:

                if candidate.upper().startswith(prefix):

                    score += 50

                    break

            scores[candidate] += score

    return scores


def choose_best_candidate(scores):

    if not scores:
        return None

    filtered_scores = {}

    for candidate, score in scores.items():

        keep = True

        for other, other_score in scores.items():

            if candidate == other:
                continue

            if (
                candidate in other
                and len(other) > len(candidate)
                and other_score >= score
            ):
                keep = False
                break

        if keep:
            filtered_scores[candidate] = score

    code, score = max(
        filtered_scores.items(),
        key=lambda x: x[1]
    )

    return StandardData(
        raw_code=code,
        score=score
    )

def get_file_names(directory):

    file_names = []

    for root, dirs, files in os.walk(directory):

        for file in files:

            if file.lower().endswith(".pdf"):

                file_names.append(
                    os.path.join(root, file)
                )

    return file_names


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

        
