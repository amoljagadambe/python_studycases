# importing "collections" for deque operations
from collections import deque

de = deque([1, 2, 3])

'''
using append() to insert element at right end  
inserts 4 at the end of deque 
'''
de.append(4)
print(de)  # deque([1, 2, 3, 4])

'''
using appendleft() to insert element at right end  
inserts 6 at the beginning of deque
'''
de.appendleft(6)
print(de)  # output:deque([6, 1, 2, 3, 4])

'''
using pop() to delete element from right end  
deletes 4 from the right end of deque
'''
de.pop()
print(de)  # output:deque([6, 1, 2, 3])

'''
using popleft() to delete element from left end  
deletes 6 from the left end of deque 
'''
de.popleft()
print(de)  # output:deque([1, 2, 3, 4])
