class Person:
    pass


person = Person()

# person.first = "amol"
# print(person.first)

first_key = 'first'
first_value = "amol"

# setattr(object, key,value)
setattr(person, first_key, first_value)
print(person.first)
firsts = getattr(person, first_key)
# print(firsts)


person_info = {'first': "amol", 'last': "jagadambe"}

for key, value in person_info.items():
    setattr(person, key, value)

# print(person.first, end =" ")
# print(person.last)

# print The object attribute using the loop

for key in person_info.keys():
    print(getattr(person, key), end=" ")
