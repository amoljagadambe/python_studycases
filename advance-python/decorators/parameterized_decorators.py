from functools import wraps


# demo decorator for cache
def check_cache(max_value):
    def decor(fn):
        print('into decorator')

        @wraps(fn)  # this will help to keep the signature of function intact like doc_string
        def wrapper(*args, **kwargs):
            print(f'max_value={max_value}')
            return fn(*args, **kwargs)

        return wrapper

    return decor


@check_cache(max_value=2014)
def divide(a: int, b: int) -> float:
    """
    returns the divide
    """
    return a / b


if __name__ == "__main__":
    print('Division is : {}'.format(divide(45782, 15)))
