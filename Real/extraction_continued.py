import re, os

def normalise_code(code):

    code = code.strip().upper()

    # BS EN -> EN
    code = re.sub(
        r'^BS\s+EN\s+',
        'EN ',
        code
    )

    # GEGN8646 -> GEGN 8646
    code = re.sub(
        r'^(GEGN)(\d+)$',
        r'\1 \2',
        code
    )

    # GM/RC1500 -> GM/RC/1500
    code = re.sub(
        r'^(GM)/([A-Z]+)(\d+)$',
        r'\1/\2/\3',
        code
    )

    # GE/RT8270 -> GE/RT/8270
    code = re.sub(
        r'^(GE)/([A-Z]+)(\d+)$',
        r'\1/\2/\3',
        code
    )

    tokens = re.split(
        r'[/\s]+',
        code
    )

    #
    # Join trailing numeric sections into part numbers
    #
    for i, token in enumerate(tokens):

        if (
            token.isdigit()
            and len(token) >= 4
        ):

            prefix = tokens[:i]
            suffix = tokens[i:]

            code = (
                "/".join(prefix)
                + "/"
                + "-".join(suffix)
            )

            break

    parts = []

    for token in re.split(
        r'[/\s]+',
        code
    ):

        # Preserve multipart numbers
        if re.fullmatch(
            r'\d+(?:-\d+)+',
            token
        ):
            parts.append(token)

        elif re.fullmatch(
            r'[A-Z]+\d+',
            token
        ):
            parts.append(token)

        else:
            parts.extend(
                p for p in token.split('-')
                if p
            )

    return "_".join(parts)

def build_filename(metadata):
    """Construct a new filename based on the extracted metadata.
        Args:
            metadata (StandardData): An instance of StandardData containing the extracted metadata.
        Returns:
            str: The constructed filename."""
    
    if metadata.year is None:
        return metadata.normalised_code

    filename = (
        f"{metadata.normalised_code}_"
        f"{metadata.year}"
    )

    if metadata.amendment:

        filename += (
            f"_{metadata.amendment}"
        )

        if metadata.amendment_year:

            filename += (
                f"_{metadata.amendment_year}"
            )

    return filename

def extract_designation_metadata(pages, raw_code):

    metadata = {
        "year": None,
        "amendment": None,
        "amendment_year": None
    }

    text = "\n".join(
        page["text"]
        for page in pages
    )

    escaped_code = re.escape(raw_code)

    #
    # 1. ISH standards
    # IEC 62271-1:2017/ISH1:2021
    #

    ish_match = re.search(
        escaped_code +
        r'.*?:(\d{4})'
        r'.*?ISH\d*[:\-]?(\d{4})',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if ish_match:

        metadata["year"] = int(
            ish_match.group(1)
        )

        metadata["amendment"] = "ISH"

        metadata["amendment_year"] = int(
            ish_match.group(2)
        )

        return metadata


    #
    # 2. Amendment standards
    # EN 55032:2015+A11:2020
    # IEC 62271-1:2017+AMD1:2021
    #

    amendment_match = re.search(
        escaped_code +
        r'.*?:(\d{4})'
        r'.*?(A\d+|AMD\d+)[:\-]?(\d{4})',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if amendment_match:

        metadata["year"] = int(
            amendment_match.group(1)
        )

        metadata["amendment"] = (
            amendment_match.group(2)
            .upper()
        )

        metadata["amendment_year"] = int(
            amendment_match.group(3)
        )

        return metadata

    #
    # 3. Explicit Date fields
    #

    date_match = re.search(
        r'DATE\s*:?\s*.*?((?:19|20)\d{2})',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if date_match:

        metadata["year"] = int(
            date_match.group(1)
        )

    #
    # Remove compliance dates before generic searches
    #

    text_without_compliance = re.sub(
        r'COMPLIANCE\s+DATE\s*:?.*?(?:19|20)\d{2}',
        '',
        text,
        flags=re.IGNORECASE | re.DOTALL
    )

    #
    # 4. Standard designation
    #
    # EN 55032:2015
    # IEC 61439-1:2021
    #

    if metadata["year"] is None:

        year_match = re.search(
            escaped_code +
            r'.{0,50}?((?:19|20)\d{2})',
            text_without_compliance,
            re.IGNORECASE | re.DOTALL
        )

        if year_match:

            metadata["year"] = int(
                year_match.group(1)
            )

    #
    # 5. Fallback
    #

    if metadata["year"] is None:

        all_years = []

        page_weights = {
            1: 50,
            2: 25,
            3: 10,
            4: 5,
            5: 1
        }

        for page in pages:

            years = re.findall(
                r'\b(?:19|20)\d{2}\b',
                page["text"]
            )

            for year in years:

                score = page_weights.get(
                    page["page"],
                    1
                )

                all_years.append(
                    (
                        score,
                        int(year)
                    )
                )

        if all_years:

            metadata["year"] = max(
                all_years,
                key=lambda x: x[0]
            )[1]

    return metadata

import os


def rename_file(old_path, standard):
    """
    Rename a PDF using standard.filename.

    Returns:
        tuple: (success, message)
    """

    if not os.path.exists(old_path):
        return (
            False,
            f"Source file does not exist: {old_path}"
        )

    if not old_path.lower().endswith(".pdf"):
        return (
            False,
            "Source file is not a PDF"
        )

    if standard is None:
        return (
            False,
            "No StandardData object supplied"
        )

    if not standard.filename:
        return (
            False,
            "No generated filename"
        )

    new_path = os.path.join(
        os.path.dirname(old_path),
        standard.filename + ".pdf"
    )

    # normcase helps on Windows, where filenames are case-insensitive.
    old_comparison = os.path.normcase(
        os.path.abspath(old_path)
    )

    new_comparison = os.path.normcase(
        os.path.abspath(new_path)
    )

    if old_comparison == new_comparison:
        return (
            True,
            "Already correctly named"
        )

    if os.path.exists(new_path):
        return (
            False,
            f"Target already exists: {new_path}"
        )

    os.rename(
        old_path,
        new_path
    )

    return (
        True,
        new_path
    )