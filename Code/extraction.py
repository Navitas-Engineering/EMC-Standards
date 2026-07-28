import fitz
import re
import os
from collections import defaultdict
from pathlib import Path
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
    "GLGN",
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
        "TABLE",
        "GEL"
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

        r'\b(?:GE|GL)[\s/_-]*GN[\s/_-]*\d+\b',

        r'\bGLGN\d+\b',

        r'\bBR\s+\d+\b',

        r'NR(?:/[A-Z0-9]+){2,5}/\d+(?:-\d+)?',

        r'RT(?:/[A-Z0-9]+){2,5}/\d+(?:-\d+)?',

        r'[A-Z]{2,}(?:[-/][A-Z0-9]+){2,}',

        r'(?:BS\s+)?EN\s+\d+(?:-\d+)*',

        r'IEC\s+\d+(?:-\d+)*',

        r'GM/[A-Z]+\d+',

        r'GE[/\s][A-Z]{2,5}\d+',

        #r'\b[A-Z]{2,5}\s+\d{3,}\b'    

        r'(?:FPRTS|PRTS|TS)\s+\d+(?:-\d+)+'

        ]

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

def canonicalise_candidate(candidate):
    """
    Canonicalise equivalent GEGN and GLGN candidate spellings before
    candidates are scored.

    Examples:
        GEGN8646       -> GEGN 8646
        GE/GN/8646     -> GEGN 8646
        GE_GN_8646     -> GEGN 8646
        GE GN 8646     -> GEGN 8646

        GLGN1620       -> GLGN 1620
        GL/GN/1620     -> GLGN 1620
    """

    candidate = candidate.strip().upper()

    guidance_match = re.fullmatch(
        r"(GE|GL)"
        r"[\s/_-]*"
        r"GN"
        r"[\s/_-]*"
        r"(\d+)",
        candidate,
        re.IGNORECASE
    )

    if guidance_match:
        prefix = guidance_match.group(1).upper()
        number = guidance_match.group(2)

        return f"{prefix}GN {number}"

    return candidate

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
            candidate = canonicalise_candidate(candidate)

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

            if candidate.startswith("TS "):
                score -= 3000

            score += (
                candidate.count("-")
                * 200
            )

            if re.match(
                r'^(IEC|EN)\s+\d',
                candidate
            ):
                score += 200

            #context around candidate
            text = page_data["text"]

            window_start = max(0, position - 50)
            window_end = min(len(text), position + len(candidate) + 50)
            context = text[window_start:window_end].upper()

            if "SUPERSEDE" in context or "WITHDRAWN" in context:
                score -=300

            if "COMMITTEE REF" in context:
                score -= 2000

            if re.fullmatch(
                r'[A-Z]{2,5}/\d+/\d+',
                candidate
            ):
                score -= 2000

            for prefix in KNOWN_PREFIXES:

                if candidate.upper().startswith(prefix):

                    score += 200

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

def get_file_names(directory, rejected_directory=None):
    """
    Recursively find PDF files below directory.

    The configured Rejected directory is excluded from discovery.
    Other subfolders, including Hold, remain eligible for scanning.
    """

    file_names = []

    root_directory = Path(directory).resolve()

    rejected_path = None

    if rejected_directory is not None:
        rejected_path = Path(
            rejected_directory
        ).resolve()

    for root, dirs, files in os.walk(root_directory):
        root_path = Path(root).resolve()

        # Modify dirs in place so os.walk does not descend into
        # the configured Rejected directory.
        dirs[:] = [
            directory_name
            for directory_name in dirs
            if (
                rejected_path is None
                or (
                    root_path
                    / directory_name
                ).resolve() != rejected_path
            )
        ]

        for file in files:
            if file.lower().endswith(".pdf"):
                file_names.append(
                    str(root_path / file)
                )

    return file_names




        
