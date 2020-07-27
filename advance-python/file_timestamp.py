import os
from datetime import datetime


def get_modification_time(filename: str, wd: str) -> datetime:
    """
    input: filename: Name of file
           wd: Working Directory which contain the above file
    return: Datetime of Modification
    """
    os.chdir(wd)
    mod_timestamp = os.stat(filename).st_mtime
    return datetime.fromtimestamp(mod_timestamp).replace(microsecond=0)


# Get CWD
cwd = os.getcwd()
method_output = get_modification_time('file_timestamp.py', cwd)
print(method_output)
