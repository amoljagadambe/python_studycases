from operator import itemgetter, attrgetter, methodcaller


class Student:
    def __init__(self, name, grade, age):
        self.name = name
        self.grade = grade
        self.age = age

    def __repr__(self):
        return repr((self.name, self.grade, self.age))

    def weighted_grade(self):
        return 'CBA'.index(self.grade) / float(self.age)


student_objects = [
    Student('john', 'A', 15),
    Student('jane', 'B', 12),
    Student('dave', 'B', 10),
]

student_tuples = [
    ('john', 'A', 15),
    ('jane', 'B', 12),
    ('dave', 'B', 10),
]
by_lambda = sorted(student_objects, key=lambda student: student.age)  # Sort by Age
print(by_lambda)

by_itemgetter = sorted(student_tuples, key=itemgetter(1, 2))  # Sort by Grade and Age
print(by_itemgetter)

by_attrgetter = sorted(student_objects, key=attrgetter('grade', 'age'))  # Sort by Grade and Age by using attributes
print(by_attrgetter)
