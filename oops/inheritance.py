"""the way inheritance work know as method Resolution order:
 Method resolution order:
 |      Developer
 |      Employee
 |      builtins.object
 |
 |  Methods inherited from Employee:
 |
 |  __init__(self, first, last, pay)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |
 |  apply_raise(self)
 |
 |  fullname(self)
 |
 |  ----------------------------------------------------------------------
 |  Data descriptors inherited from Employee:
 |
 |  __dict__
 |      dictionary for instance variables (if defined)
 |
 |  __weakref__
 |      list of weak references to the object (if defined)
 |
 |  ----------------------------------------------------------------------
 |  Data and other attributes inherited from Employee:
 |
 |  num_emp = 12
 |
 |  raise_amt = 1.04

"""


class Employee(object):
    num_emp = 00
    raise_amt = 1.40

    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.email = first + '.' + last + '@gmail.com'
        self.pay = pay

        Employee.num_emp += 1

    def fullname(self):
        return '{} {}'.format(self.first, self.last)

    def apply_raise(self):
        self.pay = int(self.pay * self.raise_amt)


class Developer(Employee):
    raise_amt = 1.50

    def __init__(self, first, last, pay, pro_lang):
        super().__init__(first, last, pay)
        self.pro_lang = pro_lang


class Manger(Employee):

    def __init__(self, first, last, pay, employee=None):
        super().__init__(first, last, pay)
        if employee is None:
            self.employee = []
        else:
            self.employee = employee

    def add_emp(self, emp):
        if emp not in self.employee:
            self.employee.append(emp)

    def remove_emp(self, emp):
        if emp in self.employee:
            self.employee.remove(emp)

    def print_emp(self):
        for emp in self.employee:
            print('-->', emp.fullname())


dev1 = Developer('amol', 'jagadambe', 10000, 'python')
dev2 = Developer('yash', 'mishra', 10000, 'html')

# print(dev1.pay)
# dev1.apply_raise()
# print(dev1.pay)

# print(dev1.email)
# print(dev1.pro_lang)

# print(help(Developer))

mag1 = Manger('jon', 'doe', 60000, [dev1])

print(mag1.email)
mag1.add_emp(dev2)

# mag1.print_emp()
mag1.remove_emp(dev2)

mag1.print_emp()
print(mag1.fullname())

print(isinstance(mag1, Developer))

print(issubclass(Manger, Employee))
