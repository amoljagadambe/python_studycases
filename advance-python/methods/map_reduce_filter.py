from functools import reduce, lru_cache

l1 = [1, 2, 3, 4, 5, 6]
l2 = [10, 20, 30, 40, 50]
l3 = 'python'

map_obj = map(lambda x, y: x + y, l1, l2)  # this will be the iterator

print(list(map_obj))  # output: [11, 22, 33, 44, 55]

# Filter the  list by elements which is divisible by 2 (this will also return the iterator)
print(list(filter(lambda x: x % 2 == 0, l1)))

# calculate the factorial by using reduce
print(reduce(lambda x, y: x * y, range(1, 6)))

"""
calculate the fibonacci series by using recursion and lru_cache for memoization
"""


@lru_cache(maxsize=1024)
def cal_fib_series(n):
    if n < 2:
        return 1
    else:
        return cal_fib_series(n - 1) + cal_fib_series(n - 2)


# for i in range(20):
#     print(cal_fib_series(i), end=' ')


print(list(map(lambda x: cal_fib_series(x), range(20))))
