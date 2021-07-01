def main():
    s = "1, 2, 3, 4"
    x = s * 5
    y = str({1, 2, 3, 4}) * 6
    z = str([1, 2, 3, 4]) * 7
    a = str({1: 2, 3: 4}) * 8
    b = str((1, 2, 3, 4)) * 9
    c = "1, 2, 3, 4" * 10
    d = "  1, 2, 3, 4  ".strip() * 11
    print(x, y, z, a, b, c, d)


if __name__ == '__main__':
    main()
