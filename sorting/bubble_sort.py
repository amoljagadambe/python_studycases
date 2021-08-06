unsorted_data = [2, 7, 8, 1, 4, 5, 6]

for i in range(len(unsorted_data) - 1, 0, -1):
    for index in range(i):
        if unsorted_data[index] > unsorted_data[index + 1]:
            temp_variable = unsorted_data[index]
            unsorted_data[index] = unsorted_data[index + 1]
            unsorted_data[index + 1] = temp_variable

print(unsorted_data)