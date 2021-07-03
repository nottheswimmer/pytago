import random


def main():
    if random.random() > 0.5:
        a = 1
    else:
        a = 2

    if random.random() > 0.5:
        if random.random() > 0.5:
            b = 1
        else:
            b = 2
    else:
        b = 3

    def hello_world():
        c = 3
        print(c)

    hello_world()
    print(a, b)


if __name__ == '__main__':
    main()
