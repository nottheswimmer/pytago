def main():
    a = 3
    b = 7
    a = a + b
    print(a + b)
    another_scope()


def another_scope():
    a = 1
    b = 12
    a = a + b
    print(a + b)


if __name__ == '__main__':
    main()
