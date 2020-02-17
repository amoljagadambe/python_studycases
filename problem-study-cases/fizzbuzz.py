'''
Here we are going with the different method to optimize the solution
'''

# Method No. 1)

for i in range(1, 100):
    output = ''
    if i % 3 == 0: output += 'Fizz'
    if i % 5 == 0: output += 'Buzz'
    if output == "": output += str(i)
    print(output)
