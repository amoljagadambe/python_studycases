"""
We will define the Memoization concept explicitly and implicitly in this program
"""
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

# Method 2) implicitly using cache lru_cache
from functools import lru_cache


@lru_cache(maxsize=1000)
def fibonacci(n):
    # Check for the input is a positive integer
    if type(n) != int:
        raise TypeError('n must be of type integer')
    if n < 1:
        raise ValueError('n must be a positive integer')

    # compute the n'th term
    if n == 1:
        return 1
    elif n == 2:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


for i in range(1, 51):
    print(fibonacci(i))
