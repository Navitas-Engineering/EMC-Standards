import pandas as pd2

from extraction import (
    extract_pages,
    score_candidates,
    choose_best_candidate,
    get_file_names,
    test_single_file
)

from renaming import (
    normalise_code,
    build_filename,
    extract_designation_metadata
)

directory = r"Sample Documents"

sample_list = get_file_names(directory)

results = []

print("Found files:")
for file in sample_list:
    print(file)

print("\nProcessing...\n")

for file in sample_list:

    pages = extract_pages(file)

    scores = score_candidates(pages)

    standard = choose_best_candidate(scores)

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

    standard.normalised_code = normalise_code(
        standard.raw_code
    )

    metadata = extract_designation_metadata(
        pages,
        standard.raw_code
    )

    standard.year = metadata["year"]
    standard.amendment = metadata["amendment"]
    standard.amendment_year = metadata["amendment_year"]

    # BR documents should not have modern years
    if (
        standard.normalised_code.startswith("BR_")
        and standard.year is not None
        and standard.year > 2000
    ):
        print(
            f"WARNING: Suspicious BR year detected "
            f"({standard.year}) in {file}"
        )

        standard.year = 0

    standard.filename = build_filename(
        standard
    )

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

final_list = pd2.DataFrame(results, columns=["Original File", "Raw Code", "Normalised Code", "Filename"])

print("\nFinal List:")
print(final_list)

test_single_file(
    r"Sample Documents\GEGN_8646_2017.pdf"
)

test_single_file(
    r"Sample Documents\IEC_62271-1_2017_ISH_2021.pdf"
)

#for page in extract_pages(r"Sample Documents\IEC_62271-1_2017_ISH_2021.pdf"):
#    print("Page", page, page["text"])