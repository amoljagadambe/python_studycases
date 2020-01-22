# python oops
import datetime


class Employee(object):
    num_emp = 10
    raise_amt = 1.04

    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.email = first + '.' + last + '@gmail.com'
        self.pay = pay

        Employee.num_emp += 1

    @property
    def fullname(self):
        return '{} {}'.format(self.first, self.last)

    def apply_raise(self):
        return int(self.pay + self.raise_amt)

    @classmethod
    def set_raise_amt(cls, amount):
        cls.raise_amt = amount

    # here classmethod used as alternative constructor.
    @classmethod
    def from_string(cls, emp_str):
        first, last, pay = emp_str.split('-')
        return cls(first, last, pay)

    # if we do not call instance vaiable or class variable then it comes under the catoegry of staticmethod
    @staticmethod
    def is_workday(day):
        if day.weekday() == 5 or day.weekday() == 6:
            return 'Weekend'
        return 'workday'


emp1 = Employee('amol', 'jagadambe', 10000)
Employee.set_raise_amt(1.05)  # we can run classmethod from instance to like below

# emp1.set_raise_amt(1.07)

print(Employee.raise_amt)
print("Prperty Decoreter ------->", emp1.fullname)
print(emp1.raise_amt)

emp_str1 = 'yash-mishra-10000'
emp_str2 = 'shantanu-pachrkar-20000'

emp2 = Employee.from_string(emp_str1)
print(emp2.fullname)
print(emp2.email)
print(emp2.pay)

my_date = datetime.date(2019, 2, 20)
print(Employee.is_workday(my_date))
