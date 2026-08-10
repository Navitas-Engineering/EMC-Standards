class StandardData:
    """
    Stores information extracted from a PDF and information used to
    validate the proposed filename.
    """

    def __init__(
        self,
        raw_code=None,
        normalised_code=None,
        year=None,
        amendment=None,
        amendment_year=None,
        filename=None,
        score=0,
        source_filename=None,
        filename_hint_code=None,
        filename_hint_year=None,
        filename_hint_amendment=None,
        filename_hint_amendment_year=None,
        status="SUCCESS",
        reasons=None,
        extracted_text_length=0,
        proposed_path=None,
        rename_result=None
    ):
        self.raw_code = raw_code
        self.normalised_code = normalised_code
        self.year = year
        self.amendment = amendment
        self.amendment_year = amendment_year
        self.filename = filename
        self.score = score

        self.source_filename = source_filename
        self.filename_hint_code = filename_hint_code
        self.filename_hint_year = filename_hint_year
        self.filename_hint_amendment = filename_hint_amendment
        self.filename_hint_amendment_year = filename_hint_amendment_year

        self.status = status
        self.reasons = reasons if reasons is not None else []

        self.extracted_text_length = extracted_text_length
        self.proposed_path = proposed_path
        self.rename_result = rename_result

    def add_reason(self, reason):
        """
        Add a validation reason without creating duplicates.
        """

        if reason and reason not in self.reasons:
            self.reasons.append(reason)

    def reasons_text(self):
        """
        Return reasons in a format suitable for an Excel cell.
        """

        return "; ".join(self.reasons)

    def __repr__(self): 
        return (
            "StandardData("
            f"raw_code={self.raw_code!r}, "
            f"normalised_code={self.normalised_code!r}, "
            f"year={self.year!r}, "
            f"amendment={self.amendment!r}, "
            f"amendment_year={self.amendment_year!r}, "
            f"filename={self.filename!r}, "
            f"score={self.score!r}, "
            f"source_filename={self.source_filename!r}, "
            f"filename_hint_code={self.filename_hint_code!r}, "
            f"filename_hint_year={self.filename_hint_year!r}, "
            f"status={self.status!r}, "
            f"reasons={self.reasons!r}"
            ")"
        )

def YN(query):
    response = input(query).strip().lower()
    while response not in ['y', 'n']:
        response = input("Invalid input. Please enter 'y' or 'n': ").strip().lower()
    return response == 'y'


