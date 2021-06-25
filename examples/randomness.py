import random


def main():
    a = random.random()
    print(a)
    b = random.randrange(9000, 10000)
    print(b)
    c = random.randint(9000, 10000)
    print(c)
    items = ["Hello", 3, "Potato", "Cake"]
    print(random.choice(items))
    random.shuffle(items)
    print(items)


if __name__ == '__main__':
    main()
