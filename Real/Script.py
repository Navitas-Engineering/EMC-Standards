import pandas as pd
import os
from extraction import get_file_names
from processing import (
    process_file,
    test_single_file
)
from extraction_continued import rename_file

#------------------#
DRY_RUN = False
#------------------#


directory = r"Test Docs"

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

    if DRY_RUN:

        new_path = os.path.join(
            os.path.dirname(file),
            standard.filename + ".pdf"
        )

        print(
            f"Would rename:\n"
            f"{file}\n"
            f"to\n"
            f"{new_path}\n"
        )

    else:
        rename_file(
            file,
            standard
        )

    results.append(
        [
            file,
            standard.raw_code,
            standard.normalised_code,
            standard.filename,
            os.path.join(
                os.path.dirname(file),
                standard.filename + ".pdf"
            )
        ]
    )



final_list = pd.DataFrame(
    results,
    columns=[
        "Original File",
        "Raw Code",
        "Normalised Code",
        "Filename",
        "New Path"
    ]
)

print("\nFinal List:")
print(final_list)

# Optional export
# final_list.to_excel(
#     "RenamePreview.xlsx",
#     index=False
# )

"""test_single_file(
    r"Sample Documents\GEGN_8646_2017.pdf"
)

test_single_file(
    r"Sample Documents\IEC_62271-1_2017_ISH_2021.pdf"
)"""