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

'''
EXTENDING THE NAMEDTUPLE AS CLASS
Namedtuple objects are implemented as regular Python classes internally. 
Because they are built on top of regular classes you can even add methods
to a namedtuple’s class.
'''

Car = namedtuple('car', ['color', 'mileage'])


class ExtendedClass(Car):
    def colorcheck(self):
        if self.color == 'red':
            return '##ff000'
        else:
            return '#00000'


c_obj = ExtendedClass('black', 132.4)
c_obj1 = ExtendedClass('red', 132.4)
print(c_obj.colorcheck())  # output:#00000
print(c_obj1.colorcheck())  # output:##ff000

'''
EXTENDING THE NAMEDTUPLE INTO ANOTHER NAMEDTUPLE
The easiest way to create hierarchies of namedtuple
is to use the base tuple’s ._fields property
'''
ElectricCar = namedtuple('ElectricCar',
                         Car._fields + ('charge',))  # IMP Tips: never ever forget the , in additional tuple

e_data = ElectricCar('blue', 145.1, 45)
print(e_data.color)  # output:blue
