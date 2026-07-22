from extraction import extract_pages, score_candidates, choose_best_candidate, get_file_names, test_single_file
import numpy as np

directory = r"Sample Documents"

file_list = np.array([])
conversion_list = np.array([])
counter = 0
file_list = get_file_names(directory)
print("file_list = ", file_list)



for file in file_list:
    
    pages = extract_pages(file)

    scores = score_candidates(pages)

    best_candidate = str(choose_best_candidate(scores))

    print(f"Best candidate for {file}: {best_candidate}")
    conversion_list = np.append(conversion_list, best_candidate)

final_list = np.column_stack((file_list, conversion_list))
print ("Final list = ", final_list)


test_single_file(r"Sample Documents\GEGN_8646_2017.pdf")


pages = extract_pages(
    r"Sample Documents\GEGN_8646_2017.pdf"
)

print("First page of text:")
print(pages[0]["text"])
        
    
    
