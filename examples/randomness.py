import random


def main():
    print(random.random())
    print(random.randrange(9000, 10000))
    print(random.randint(9000, 10000))
    items = ["Hello", 3, "Potato", "Cake"]
    print(random.choice(items))
    random.shuffle(items)
    print(items)
    u = random.uniform(200, 500)
    print(u)


if __name__ == '__main__':
    main()
