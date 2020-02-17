'''
We will define the Memoization concept explicitly and implicitly in this program
'''
# Method 1) explicitly using cache dict

fibonacci_cache = {}


def fibonacci(n):
    # If we have the value of n'th term then return the value
    if n in fibonacci_cache:
        return fibonacci_cache[n]

    # compute the N'th value
    if n == 1:
        value = 1
    elif n == 2:
        value = 1
    else:
        value = fibonacci(n - 1) + fibonacci(n - 2)

    # store the value of the N'th term
    fibonacci_cache[n] = value
    return value


print("Fibonacci sequence:")
for i in range(1, 101):
    print(i, ':', fibonacci(i))
