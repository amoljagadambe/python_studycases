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


# Conversion Operations

it_list = ['Tensorflow', 'ML']
sample_dict = {'name': "PowerBI", 'technology': 'Tableu'}

'''
using _make() to return namedtuple()
_make() :- This function is used to return a namedtuple() from the iterable passed as argument.
'''
print(named_a._make(it_list))  # output : courses(name='Tensorflow', technology='ML')

'''
using _asdict() to return an OrderedDict()
_asdict() :- This function returns the OrdereDict() as constructed from the mapped values of namedtuple().
'''
print(values._asdict())  # output :  OrderedDict([('name', 'Machine Learning'), ('technology', 'python')])

'''
using ** operator to return namedtuple from dictionary
using “**” (double star) operator :- This function is used to convert a dictionary into the namedtuple().
'''
print(named_a(**sample_dict))  # output :  courses(name='PowerBI', technology='Tableu')
