import numpy as np

list_one = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
list_two = np.array(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j'])

two_d = np.column_stack((list_one, list_two))

print(two_d)