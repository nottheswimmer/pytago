def main():
    a = "hello"
    b = "world"
    c = a + " " + b
    print(c)
    print(double_it(c))
    print(c[1])
    print(c[1:6])


def double_it(c: str) -> str:
    return c + c


if __name__ == '__main__':
    main()
