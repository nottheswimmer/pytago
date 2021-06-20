def main():
    a = [x for x in range(10)]
    b = [x for x in range(10) if x % 2 == 0]
    c = [x if x % 2 == 0 else 777 for x in range(10)]
    d = [x for i, x in enumerate(c) if i % 2 == 0 if i % 3 == 1]
    e = [(x, y) for x in c for y in d]
    f = [(x, y) for x in c for y in next_five_numbers_times_two(x)]
    g = [(i, j) for i in range(10) for j in range(i)]

    print(a)
    print(b)
    print(c)
    print(d)
    print(e)
    print(f)
    print(g)


def next_five_numbers_times_two(a: int) -> list[int]:
    return [(a + i) * 2 for i in range(1, 6)]


if __name__ == '__main__':
    main()
