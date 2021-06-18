def main():
    a = increment(1)
    print(a)
    b = increment(a, 2)
    print(b)
    c = increment(a, decrement=True, amount=3)
    print(c)


def increment(n: int, amount: int = 1, decrement: bool = False) -> int:
    if decrement:
        return n - amount
    return n + amount


if __name__ == '__main__':
    main()
