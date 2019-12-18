student = {'course':'Python', 'name': 'Amol', 'roll no': 25, 'Skills': ['Python','Machine Learninig']}

print(student['roll no'])

# del student['name']
name = student.pop('name')
#pop Method Will pop the value and retrun the value also
print(name)


## important Notes

for keys in student:
    print(keys)
# Above method Will only get the keys from dict


print(student.get('course', 'Error :  Key Not Availble'))

print(student)