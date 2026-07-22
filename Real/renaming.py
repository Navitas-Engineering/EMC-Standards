import re

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

    parts = []

    for token in re.split(
        r'[/\s]+',
        code
    ):

        # Preserve numeric sections
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
    """
    Extract metadata such as year, amendment, and amendment year from the extracted pages based on the raw code.
    Args:
        pages (list): A list of dictionaries containing page numbers and extracted text.
        raw_code (str): The raw code extracted from the PDF file.
    Returns:
        dict: A dictionary containing the extracted metadata with keys 'year', 'amendment', and 'amendment_year'.
    """

    full_text = "\n".join(
    page["text"]
    for page in pages
)

    text = "\n".join(
        page["text"]
        for page in pages
    )

    metadata = {
        "year": None,
        "amendment": None,
        "amendment_year": None
    }

    escaped_code = re.escape(raw_code)

    #
    # Look near the detected code first
    #

    code_match = re.search(
        escaped_code,
        text,
        re.IGNORECASE
    )

    if code_match:

        start = max(0, code_match.start() - 100)
        end = min(len(text), code_match.end() + 250)

        window = text[start:end]

        designation_match = re.search(
            escaped_code +
            r':(\d{4}).*?ISH\d*:(\d{4})',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if designation_match:
            metadata["year"] = int(
                designation_match.group(1)
        )
            metadata["amendment"] = "ISH"

            metadata["amendment_year"] = int(
                designation_match.group(2)
            )

            return metadata

        #
        # Find all years near the code
        #

        years = re.findall(
            r'\b(?:19|20)\d{2}\b',
            window
        )

        if years:
            metadata["year"] = int(years[0])

        #
        # Amendment detection
        #

        amendment_match = re.search(
            r':(\d{4}).*?(A\d+|AMD\d+):(\d{4})',
            window,
            re.IGNORECASE
        )

        if amendment_match:

            metadata["amendment"] = (
                amendment_match.group(1)
                .upper()
            )

            amendment_pos = amendment_match.end()

            amendment_window = (
                window[
                    amendment_pos:
                    amendment_pos + 100
                ]
            )

            amendment_year_match = re.search(
                r'\b(?:19|20)\d{2}\b',
                amendment_window
            )

            if amendment_year_match:

                metadata["amendment_year"] = int(
                    amendment_year_match.group(0)
                )

        #
        # ISH detection
        #

        else:

            ish_match = re.search(
                r'\bISH\b',
                window,
                re.IGNORECASE
            )

            if ish_match:

                metadata["amendment"] = "ISH"

                ish_pos = ish_match.end()

                ish_window = (
                    window[
                        ish_pos:
                        ish_pos + 100
                    ]
                )

                ish_year_match = re.search(
                    r'\b(?:19|20)\d{2}\b',
                    ish_window
                )

                if ish_year_match:

                    metadata["amendment_year"] = int(
                        ish_year_match.group(0)
                    )

    #
    # Fallback if no year found
    #

    if metadata["year"] is None:

        all_years = []

        for page in pages:

            page_no = page["page"]

            years = re.findall(
                r'\b(?:19|20)\d{2}\b',
                page["text"]
            )

            for year in years:

                score = 0

                if page_no == 1:
                    score += 50
                elif page_no == 2:
                    score += 25
                elif page_no == 3:
                    score += 10

                score += int(year)

                all_years.append(
                    (score, int(year))
                )

        if all_years:

            metadata["year"] = max(
                all_years,
                key=lambda x: x[0]
            )[1]

    return metadata