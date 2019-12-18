def check(num):
    str(num)
    reverse = num[::-1]
    if num == reverse:
        return "palindrome"
    else:
        return "not a palindrome"


if __name__ == '__main__':
    num = input("give the Number or string:\n")
    print(check(num=num))
