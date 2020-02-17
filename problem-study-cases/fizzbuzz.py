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


# Method No. 2) This use the function and dict

def fizzbuzz(multipules, *args):
    for val in range(*args):
        out_value = ''
        for multiple in multipules:
            if val % multiple == 0:
                out_value += multipules[multiple]

        if out_value == '':
            out_value = val
        print(out_value)


multiples = {3: 'Fizz', 5: 'Buzz'}
fizzbuzz(multiples, 1, 101)
