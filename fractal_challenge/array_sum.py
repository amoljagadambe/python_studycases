def calculate_combination(num_elements: int, list_of_elements: list):
    if num_elements <= 3:
        return 0  # this covers the case where removing one element will not give sum to calculate
    possible_index_list = []

    for index, element in enumerate(list_of_elements):
        # remove element
        list_of_elements.remove(element)
        for desired_sum in list_of_elements:
            if desired_sum == sum(list_of_elements) - desired_sum:
                global no_of_combination_possible
                no_of_combination_possible += 1
                possible_index_list.append(index + 1)
        # insert element at their respective index
        list_of_elements.insert(index, element)
    possible_index_list.sort()  # sort the index in ascending order
    return possible_index_list


if __name__ == "__main__":

    """
    uncomment below line for test input to the function and pass it to see the output. not been able to 
    write parameterized test cases due to time constraints
    """
    # num_arrays_test = 6
    # list_of_numbers_test = [4, 7, 1, 1, 1, 1]

    no_of_combination_possible = 0
    num_of_arrays = int(input())   # Input the number of elements on array
    list_of_numbers = list(map(int, input().split()))  # Input for the number of elements in array

    combinations = calculate_combination(num_of_arrays, list_of_numbers)
    if no_of_combination_possible > 0:
        print(no_of_combination_possible)
        print(*combinations, sep=" ")
    else:
        print(no_of_combination_possible)
