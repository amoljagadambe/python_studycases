from collections import Counter

string = 'amoljagadambeasdweqfghjl'

out_count_list = [values for values in string]

count_dict = Counter(out_count_list)
print(count_dict)
print(type(count_dict))