from collections import namedtuple

'''
Attributes Accepted by Namedtuple
namedtuple(typename, field_names, *, verbose=False, rename=False, module=None)
'''

named_a = namedtuple('courses', ['name', 'technology'])
values = named_a('Machine Learning', 'python')

'''
Namedtuple access methods
'''
# Access using name
print(values.name)  # output : Machine Learning

# Access using index
print(values[1])  # output : python

# Access using getattr()
print(getattr(values, 'name'))  # output : Machine Learning
