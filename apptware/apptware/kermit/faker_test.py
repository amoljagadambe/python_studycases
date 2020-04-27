#
# dict_vaule = {'asmd':124,'awed':654}
#
# x_col = [k for k in dict_vaule.keys() if k.startswith('a')]
# # print(x_col)
#
#
# list_dict = [{"a": 24, "age": [94, 170], "c": 'Hello Iam Amol'}, {"a": 21, "age": [23,56], "c": 'Hello Iam yash'}]
#
# # x_col = ['age', 'weight']
# #
# # dict['note_textL'] = dict['c'].split()
# # thres = 23
# # dict['decision'] = 'True' if dict['a'] < thres else 'False'
# # print(dict)
#
# for dict in list_dict:
#     print(dict['age'])

a = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
iter_func = iter(a)

for i in range(9):
    c = next(iter_func) // 2
print(c)
