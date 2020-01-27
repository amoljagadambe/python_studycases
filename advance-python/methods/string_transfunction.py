import string

thirdString = string.punctuation

str_in = "this is string example....wow!!!"
transtab = str.maketrans(' ', ' ', thirdString)
# print(transtab)
out = str_in.translate(transtab)

print(out)