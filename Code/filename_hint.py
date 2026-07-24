import os
import re


def normalise_hint_text(text):
    """
    Remove spaces and punctuation so differently formatted codes can
    be compared.

    Examples:
        GE_RT_8270       -> GERT8270
        GE RT8270        -> GERT8270
        NR/L2/ELP/27716  -> NRL2ELP27716
    """

    if not text:
        return ""

    return re.sub(
        r"[^A-Z0-9]",
        "",
        str(text).upper()
    )


def extract_filename_hint(file_path):
    """
    Extract useful hints from the current filename.

    The filename is only a hint. It is not used as the automatic
    source of truth.
    """

    filename = os.path.basename(file_path)
    stem = os.path.splitext(filename)[0]

    result = {
        "source_filename": filename,
        "stem": stem,
        "code": None,
        "year": None,
        "amendment": None,
        "amendment_year": None,
        "years": []
    }

    # Find plausible years anywhere in the filename.
    # Digit lookarounds prevent numbers such as 27716 from being
    # interpreted as a four-digit year.
    year_matches = re.findall(
        r"(?<!\d)((?:19|20)\d{2})(?!\d)",
        stem
    )

    result["years"] = [
        int(year)
        for year in year_matches
    ]

    # Standard library format with amendment:
    # EN_55032_2015_A11_2020
    # IEC_62271-1_2017_ISH_2021
    amendment_match = re.match(
        r"^(.*?)"
        r"[_\s-]+((?:19|20)\d{2})"
        r"[_\s-]+(ISH\d*|A\d+|AMD\d+)"
        r"[_\s-]+((?:19|20)\d{2})$",
        stem,
        re.IGNORECASE
    )

    if amendment_match:
        result["code"] = amendment_match.group(1).strip(" _-")
        result["year"] = int(amendment_match.group(2))

        amendment = amendment_match.group(3).upper()

        # Treat ISH1, ISH2 etc. as library suffix ISH.
        if amendment.startswith("ISH"):
            amendment = "ISH"

        # Convert AMD1 to A1 to match your filename convention.
        if amendment.startswith("AMD"):
            amendment = "A" + amendment[3:]

        result["amendment"] = amendment
        result["amendment_year"] = int(amendment_match.group(4))

        return result

    # Standard library format without amendment:
    # EN_55032_2015
    # GE_RT_8270_2007
    standard_match = re.match(
        r"^(.*?)[_\s-]+((?:19|20)\d{2})$",
        stem,
        re.IGNORECASE
    )

    if standard_match:
        result["code"] = standard_match.group(1).strip(" _-")
        result["year"] = int(standard_match.group(2))

        return result

    # Less structured filename.
    #
    # Keep the complete filename stem for contains matching.
    result["code"] = stem

    # If there is only one year, it is a useful publication-year hint.
    if len(result["years"]) == 1:
        result["year"] = result["years"][0]

    # If there are multiple years, the first is tentatively treated
    # as the publication year. Validation still treats this as a hint.
    elif len(result["years"]) > 1:
        result["year"] = result["years"][0]

    return result


def filename_contains_code(filename_text, extracted_code):
    """
    Return True when the cleaned extracted code is contained within
    the cleaned current filename.

    This is deliberately more forgiving than exact matching.
    """

    cleaned_filename = normalise_hint_text(filename_text)
    cleaned_code = normalise_hint_text(extracted_code)

    if not cleaned_filename or not cleaned_code:
        return False

    return cleaned_code in cleaned_filename