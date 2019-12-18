import time
from threading import *
import threading


# Method 1) Creating the Thread Without Creating the class

def new():
    for i in range(6):
        '''print("Child Executing", current_thread().getName())'''


t1 = Thread(target=new)
t1.start()  # Child Threads Created
t1.join()  # This Will Wait Till The Child Thread  Completes it's Execution


# print("Bye", current_thread().getName())


# Method 2)  By Extending the Thread Class

class A(threading.Thread):
    def run(self):
        for i in range(7):
            '''print("Child is Running", current_thread().getName())'''


obj = A()
obj.start()
obj.join()


# print("Control Return to:", current_thread().getName())


# Method 3) By without extending the Thread Class

class ex:
    def B(self):
        lst = [2, 1, 'Bye', "jane"]
        for x in lst:
            '''print("Child Printing :", x)'''


myobj = ex()
t1 = Thread(target=myobj.B())
t1.start()
t1.join()


# print("Control Return to :", current_thread().getName())

# Time Comparison

def d2(n):
    for x in n:
        print(x % 2)


def d3(n):
    for i in n:
        print(i % 3)


n = [18, 27, 50, 5, 7]
s = time.time()

t1 = Thread(target=d2, args=(n,))
t2 = Thread(target=d3, args=(n,))
t1.start()
t2.start()
end = time.time()
print("Total time Taken:", end - s)


# Time Taken Without threads Total time Taken: 0.002587
#Time Taken threads Total time Taken:0.0009999275207519531