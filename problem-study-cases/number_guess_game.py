# Random lib to generate a random int
import random

n = 500
# random.seed(random.random())
guessed = random.getrandbits(8)
guess = 0

while guess != guessed:
    try:
        guess = int(input("Enter the guessing number:\t"))
        if guess > guessed:
            print("number is smaller")
        elif guess < guessed:
            print("number is greater")
    except KeyboardInterrupt:  # This will catch ctrl-c interrupt
        print("\nYour Giving UP")
        exit(0)

print("Congrats you find the number:", guess)
