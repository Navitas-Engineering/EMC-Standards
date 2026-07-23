import pandas as pd

from extraction import get_file_names
from processing import (
    process_file,
    test_single_file
)

directory = r"Sample Documents"

sample_list = get_file_names(directory)

results = []

print("Found files:")
for file in sample_list:
    print(file)

print("\nProcessing...\n")

for file in sample_list:

    standard = process_file(file)

    if standard is None:

        print(f"No candidate found for {file}")

        results.append(
            [
                file,
                None,
                None,
                None
            ]
        )

        continue

    print(
        f"{file} -> {standard.filename}"
    )

    results.append(
        [
            file,
            standard.raw_code,
            standard.normalised_code,
            standard.filename
        ]
    )

final_list = pd.DataFrame(
    results,
    columns=[
        "Original File",
        "Raw Code",
        "Normalised Code",
        "Filename"
    ]
)

print("\nFinal List:")
print(final_list)

# Optional export
# final_list.to_excel(
#     "RenamePreview.xlsx",
#     index=False
# )

test_single_file(
    r"Sample Documents\GEGN_8646_2017.pdf"
)

test_single_file(
    r"Sample Documents\IEC_62271-1_2017_ISH_2021.pdf"
)