# importing "collections" for deque operations
from collections import deque

de = deque([1, 2, 3, 3, 4, 2, 4, 2])

'''
using append() to insert element at right end  
inserts 4 at the end of deque 
'''
de.append(4)
print(de)  # output:deque([1, 2, 3, 3, 4, 2, 4, 2, 4])

'''
using appendleft() to insert element at right end  
inserts 6 at the beginning of deque
'''
de.appendleft(6)
print(de)  # output:deque([6, 1, 2, 3, 3, 4, 2, 4, 2, 4])

'''
using pop() to delete element from right end  
deletes 4 from the right end of deque
'''
de.pop()
print(de)  # output:deque([6, 1, 2, 3, 3, 4, 2, 4, 2])

'''
using popleft() to delete element from left end  
deletes 6 from the left end of deque 
'''
de.popleft()
print(de)  # output:deque([1, 2, 3, 3, 4, 2, 4, 2])

'''
index(element, begin, end) :- This function returns the 
first index of the value mentioned in elements, 
starting searching from begin till end index.
'''
# using index() to print the first occurrence of 4
print('index=', de.index(4, 5, 7))  # output: index=6

# using insert() to insert the value 3 at 5th position
de.insert(4, 3)
print(de)  # output:deque([1, 2, 3, 3, 3, 4, 2, 4, 2])

# using remove() to remove the first occurrence of 3
de.remove(3)
print(de)  # output:deque([1, 2, 3, 3, 4, 2, 4, 2])

# count() function counts the number of occurrences of value mentioned in arguments.
print(de.count(3))