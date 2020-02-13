from collections import Counter

# With sequence of items
data = ['B', 'B', 'A', 'B', 'C', 'A', 'B', 'B', 'A', 'C']
out_data = Counter(data)
print(out_data)  # output:Counter({'B': 5, 'A': 3, 'C': 2})

# with keyword arguments
print(Counter(A=3, B=5, C=2))  # output:Counter({'B': 5, 'A': 3, 'C': 2})

# Creating the empty counter

count = Counter()
count.update(data)
print(count)  # output:Counter({'B': 5, 'A': 3, 'C': 2})

# adding the value into same count

count.update(['A', 'C', 'Z'])
print(count)  # output:Counter({'B': 5, 'A': 4, 'C': 3, 'Z': 1})

# Counter subtraction
count.subtract(out_data)
print(count)  # output:Counter({'A': 1, 'C': 1, 'Z': 1, 'B': 0})

