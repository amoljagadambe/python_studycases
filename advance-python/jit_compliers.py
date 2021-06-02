from numba import jit, vectorize
import numpy as np
import time

x = np.arange(10000).reshape(100, 100)


@jit(nopython=True)
def go_fast(a):  # Function is compiled and runs in machine code
    trace = 0.0
    for i in range(a.shape[0]):
        trace += np.tanh(a[i, i])
    return a + trace


# DO NOT REPORT THIS... COMPILATION TIME IS INCLUDED IN THE EXECUTION TIME!
start = time.time()
go_fast(x)
end = time.time()
print("Elapsed (with compilation) = %s" % (end - start))

# NOW THE FUNCTION IS COMPILED, RE-TIME IT EXECUTING FROM CACHE
start = time.time()
go_fast(x)
end = time.time()
print("Elapsed (after compilation) = %s" % (end - start))

test_array = np.arange(5000)


@vectorize()
def scaler_com(num):
    if num % 2 == 0:
        return 2
    else:
        return 1


start = time.time()
print(scaler_com(test_array))
end = time.time()
print("Elapsed (after compilation) = %s" % (end - start))
