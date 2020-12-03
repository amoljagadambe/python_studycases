import time


# decorator to calculate duration
# taken by any function.
def calculate_time(func):
    # added arguments inside the inner1,
    # if function takes any arguments,
    # can be added like this.
    def wrapper(*args, **kwargs):
        # storing time before function execution
        begin = time.time()

        func_output = func(*args, **kwargs)
        # storing time after function execution
        end = time.time()
        print("Elapsed time: {0:0.2f} seconds".format(end - begin))
        return func_output

    return wrapper


@calculate_time
def multiplication(a, b):
    # sleep 1 seconds because it takes very less time
    # so that you can see the actual difference
    time.sleep(1)
    return a * b


if __name__ == "__main__":
    print('Multiplication is : {}'.format(multiplication(8, 20)))  # output > 1 Second because of sleep time
