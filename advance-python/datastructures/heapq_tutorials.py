import heapq


li_data = [5, 7, 9, 1, 3]

# using heapify to convert list into heap
heapq.heapify(li_data)
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