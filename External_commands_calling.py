import subprocess
import os

with open('output.txt', 'w') as f:
    p1 = subprocess.run('dir', stdout=subprocess.PIPE, shell=True)
print(p1.args)
print(p1.stdout)
 