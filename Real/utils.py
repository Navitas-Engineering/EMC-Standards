class StandardData:
    """Class to hold standard metadata. Stores the raw code, normalised code, year, amendment no., amendment year, filename and score for a standard.
    Attributes:
        raw_code (str): The original code extracted from the PDF file, before any normalisation or reformatting.
        normalised_code (str): New filename.
        year (int): Year of publication.
        amendment (str): Amendment number.
        amendment_year (int): Year of amendment.
        filename (str): Old filename.
        score (int): Used for scoring"""

    def __init__(self, raw_code: str, normalised_code: str = None, year: int = None, amendment: str = None, amendment_year: int = None, filename: str = None, score: int = 0):
        self.raw_code = raw_code
        self.normalised_code = normalised_code
        self.year = year
        self.amendment = amendment
        self.amendment_year = amendment_year
        self.filename = filename
        self.score = score

    def __repr__(self):
        return(
        f"StandardData("
        f"raw_code='{self.raw_code}', "
        f"normalised_code='{self.normalised_code}', "
        f"year={self.year}, "
        f"amendment={self.amendment}, "
        f"amendment_year={self.amendment_year}, "
        f"filename='{self.filename}', "
        f"score={self.score}"
        f")"
    )

    

     