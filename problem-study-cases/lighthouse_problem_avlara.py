def check_left(index, mapping):
    number_of_visible_lh = 0
    if index == 1:
        return number_of_visible_lh
    else:
        for i in range(index - 1, 0, -1):
            if mapping.get(i) >= mapping.get(index):
                break
            else:
                number_of_visible_lh += 1
    return number_of_visible_lh


def check_right(index, mapping):
    number_of_visible_lh = 0
    if index == no_of_lighthouses:
        return number_of_visible_lh
    else:
        for i in range(index + 1, no_of_lighthouses + 1):
            if mapping.get(i) >= mapping.get(index):
                break
            else:
                number_of_visible_lh += 1
    return number_of_visible_lh


def get_range_of_lighthouse(mapping):
    range_of_lh = []
    for index in range(1, no_of_lighthouses + 1):
        number_of_lf_lh = check_left(index, mapping)
        number_of_rh_lh = check_right(index, mapping)
        a = number_of_lf_lh + number_of_rh_lh
        range_of_lh.append(a * index)
    max_value = max(range_of_lh)
    max_index = range_of_lh.index(max_value)
    return max_index + 1


t = int(input())
output_list = []
for case in range(t):
    no_of_lighthouses = int(input())
    hight_of_lighthouses = map(int, input().split())
    lh_map_to_higth = {k: v for k, v in enumerate(hight_of_lighthouses, 1)}
    output = get_range_of_lighthouse(lh_map_to_higth)
    output_list.append(output)

for highest_index in output_list:
    print(highest_index)
