def main():
    a = [1, 2, 3]
    b = map(increment, a)
    for value in b:
        print(value)


def increment(n: int) -> int:
    return n + 1


if __name__ == '__main__':
    main()
