names = ['amol', 'yash', 'rahul', 'ashutosh']

for index, name in enumerate(names, start=1):
    print(index, name)

# Looping two list at time suing enumrate

h_name = ['peter parkar', 'clark kent', 'wade wilson', 'bruse wayne']
heros = ['spiderman', 'superman', 'deadpool', 'batman']
combination = {}
for name, hero in zip(h_name, heros):
    combination[name] = hero
    print(f'{name} is actually {hero}.')
print(combination)


#Tuple Unpacking

a , b ,*c = (1,2,4,8,9,7)
print(a,b,c)
print(type(c))