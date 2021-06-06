def main():
    a = 7
    b = add(a, -2)
    if a > b:
        print("It's bigger")
    elif a == b:
        print("They're equal")
    else:
        print("It's smaller")


def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    main()
