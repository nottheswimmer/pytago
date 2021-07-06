def fib(n):
    a, b = 0, 1
    while a < n:
        print(a, end=' ')
        a, b = b, a + b
    print()


def main():
    fib(1000)
    print("All done!", end='')


if __name__ == '__main__':
    main()
