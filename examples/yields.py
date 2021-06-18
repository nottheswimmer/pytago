def main():
    my_gen = gen()
    for x in my_gen:
        print("Received next number!")
        print(x)


def gen():
    print("Yielding next number...")
    yield 1
    print("Yielding next number...")
    yield 2
    print("Yielding next number...")
    yield 3


if __name__ == '__main__':
    main()
