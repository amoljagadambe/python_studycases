import os
from contextlib import contextmanager


# change the current working directory
# to specified path

@contextmanager
def change_dir(destination):
    try:
        cwd = os.getcwd()
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)


with change_dir('C:\project\Study\python_studycases\command line'):
    print(os.listdir())

with change_dir('C:\project\Study\python_studycases\multithreading'):
    print(os.listdir())