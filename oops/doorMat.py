N = 9
M = 27
sub = '.|.'
sub_string = 'WELCOME'
loop = int((M-len(sub))/2)
for k in range(0, int((N-1)/2)):
    for _ in range(0, loop):
        print("-", end="")

    for _ in range(0, 1+(k*2)):
        print(sub,end="")
    for _ in range(0, loop):
        print("-", end="")
    loop = loop-3
    print('\n')

loop1 = int((M-len(sub_string))/2)
for _ in range(0, loop1):
    print("-", end="")

for _ in range(0,1):
    print(sub_string,end="")

for _ in range(0,loop1):
    print("-", end="")
print('\n')
loop2 = int(N/3)
for i in range(4, 0, -1):
    for _ in range(0,loop2):
        print("-", end="")

    for _ in range(0, (i*2)-1):
        print(sub, end="")
    for _ in range(0, loop2):
        print("-", end="")
    loop2=loop2+3
    print('\n')
