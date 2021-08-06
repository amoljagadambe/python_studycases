unsorted_data = [2, 7, 17, 11, 56, 45, 89, 8, 1, 5, 6, 79]


def selection_sort(unsorted_list: list):
    for i in range(len(unsorted_list) - 1):
        min_position = i
        for j in range(i, len(unsorted_list)):
            if unsorted_list[j] < unsorted_list[min_position]:
                min_position = j

        temp_variable = unsorted_list[i]
        unsorted_list[i] = unsorted_list[min_position]
        unsorted_list[min_position] = temp_variable
    return unsorted_list


def merge_sort(list_data: list):
    # TODO: work on indexOutOfBound Exception if one of the list exhaust first
    middle = (len(list_data) - 1) // 2
    print(middle)
    first_half = selection_sort(list_data[:middle])
    second_half = selection_sort(list_data[middle + 1:])
    print(first_half, second_half)
    output_list = []
    i = j = 0
    for index in range(len(list_data) - 1):
        if first_half[i] <= second_half[j]:
            output_list.insert(index, first_half[i])
            if i == len(first_half)-1:
                print(i)
                output_list.insert(index, second_half[j])
                j += 1
                # i -= 1
            else:
                i += 1
        else:
            output_list.insert(index, second_half[j])
            j += 1
    return output_list


output_data = merge_sort(unsorted_data)
print(output_data)