import itertools
input_list = [
         {'a':'tata', 'b': 'bar'},
         {'a':'tata', 'b': 'foo'},
         {'a':'pipo', 'b': 'titi'},
         {'a':'pipo', 'b': 'toto'},

 ]
# data = {k:[v for v in input_list if v['a'] == k] for k, val in itertools.groupby(input_list,lambda x: x['a'])}
# print(data)
for k, val in itertools.groupby(input_list,lambda x: x['a']):
    print("--", k, "--")
    for things in val:
        print(things)