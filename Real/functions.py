import fitz
import re
import os
from collections import defaultdict
import numpy as np

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



pdf_path = r"Incoming\NR_SP_ELP_27224_2006.pdf"

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
        "PAGE"
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

        r'[A-Z]{2,}(?:[-/][A-Z0-9]+){2,}',

        r'[A-Z]{2,}(?:/[A-Z0-9]+){1,5}/?\d*',

        r'(?:BS\s+)?EN\s+\d+(?:-\d+)*',

        r'IEC\s+\d+(?:-\d+)*'
    ]

    candidates = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            page_text,
            re.IGNORECASE
        )

        candidates.extend(matches)

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
        1: 50,
        2: 25,
        3: 10,
        4: 5,
        5: 1
    }

    for page_data in pages:

        page_no = page_data["page"]

        candidates = find_candidates(
            page_data["text"]
        )

        for candidate in candidates:

            candidate = candidate.strip()

            if is_junk_candidate(candidate):
                continue
            
            score = 0

            # Appears on early page
            score += page_weights.get(
                page_no,
                1
            )

            if "/" in candidate:
                score += 10

            if re.search(
                r'\d{3,}',
                candidate
            ):
                score += 10

            for prefix in KNOWN_PREFIXES:

                if candidate.upper().startswith(prefix):

                    score += 20

                    break

            scores[candidate] += score

    return scores


def choose_best_candidate(scores):

    if not scores:

        return None

    return max(
        scores.items(),
        key=lambda x: x[1]
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

