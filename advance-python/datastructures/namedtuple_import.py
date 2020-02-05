from collections import namedtuple

'''
Attributes Accepted by Namedtuple
namedtuple(typename, field_names, *, verbose=False, rename=False, module=None)
'''

named_a = namedtuple('courses', ['name', 'technology'])
values = named_a('Machine Learning', 'python')
print(values)
