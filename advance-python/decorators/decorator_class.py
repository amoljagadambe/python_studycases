from functools import wraps


class MyClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __call__(self, fn):
        """
        this method will help to call object created by the class
        ex:
        obj = MyClass(10,20)
        obj()
        """

        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f'Decorated function called: a={self.a}, b={self.b}')
            return fn(*args, **kwargs)

        return wrapper


@MyClass(100, 200)
def hello_func(s):
    print(f'Hello {s}')


if __name__ == "__main__":
    hello_func('world')
