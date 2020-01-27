def simplegenraterr(value):
    yield value
    yield value + 1
    yield value + 2

x_obj = simplegenraterr(5)

#We can call generater using __next__ function

# print(x_obj.__next__())
# print(x_obj.__next__())
# print(x_obj.__next__())

''' ouptut
5
6
7'''

#another method is to use looping statement

for data in simplegenraterr(6):
    print(data, end=" ")

'''output
6 7 8 '''

print('\n')


def fibonogenrater(limit):
    a, b = 0, 1
    while a < limit:
        yield a
        a, b = b, a + b


for values in fibonogenrater(20):
    print(values, end=" ")
