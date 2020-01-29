import subprocess

#This Code will not run on windows

#Redircting ouput to the File
# with open('output.txt','w') as f:
#     out = subprocess.run(['dir'], stdout=f, shell=True)

out = subprocess.run(['dir'], stdout=subprocess.PIPE, shell=True)

print(out.stdout.decode())