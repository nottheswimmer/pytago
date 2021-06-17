SITE = "https://www.google.com/"
NAME = ["Michael", "Wayne", "Phelps"]
KEYS = {1: 2, 3: 4}
AGE = 1000
BIRTH_YEAR = 2050


def main():
    global AGE
    print(SITE)
    print(NAME)
    print(BIRTH_YEAR)
    print(KEYS)
    print(AGE)
    AGE = 20  # This should use the variable from the global scope
    other_1()
    print(AGE)
    other_2()


def other_1():
    AGE = 200  # This should declare a new variable age
    print(AGE)

def other_2():
    print(AGE)  # This should still be able to access the global


if __name__ == '__main__':
    main()
