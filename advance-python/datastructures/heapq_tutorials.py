import heapq

li_data = [5, 7, 9, 1, 3]
li = [5, 7, 9, 4, 3, 1]

# using heapify to convert list into heap
heapq.heapify(li_data)
heapq.heapify(li)
print(li_data)

'''
using heappush() to push elements into heap 
pushes 4
'''
heapq.heappush(li_data, 4)
print(li_data)

'''
using heappop() to pop smallest element
function is used to remove and return the 
smallest element from heap. 
'''
print(heapq.heappop(li_data))

'''
using heappushpop() to push and pop items simultaneously
pops 2
'''
print(heapq.heappushpop(li, 2))

'''
using heapreplace() to push and pop items simultaneously
element is first popped, then element is pushed.i.e, the 
value larger than the pushed value can be returned.
'''
print(heapq.heapreplace(li, 5))

'''
 function is used to return the k largest elements from 
 the iterable specified and satisfying the key if mentioned.
 returns the list
'''
largest = heapq.nlargest(3, li)
print(largest)  # output: [9, 7, 5]

'''
unction is used to return the k smallest elements from 
the iterable specified and satisfying the key if mentioned.
'''
smallest = heapq.nsmallest(2, li_data)
print(smallest)  # output:[3, 4]
