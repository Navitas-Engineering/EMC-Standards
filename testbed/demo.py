import fitz
import re

pdf_path = r"Incoming\NR_SP_ELP_27224_2006.pdf"

doc = fitz.open(pdf_path)

meta = doc.metadata
print("metadata = ", meta)


text = doc[0].get_text()

match = re.search(
    r"NR/[A-Z0-9]+/[A-Z0-9]+/\d+",
    text
)

if match:
    print(match.group())
else:
    print("No code found")

year_match = re.search(
    r"(19|20)\d{2}",
    text
)

if year_match:
    print(year_match.group())

raw_code = match.group()

standard_code = (
    raw_code.replace("/", "_")
    + "_"
    + year_match.group()
)

print(standard_code)


