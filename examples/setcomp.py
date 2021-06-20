def main():
    a = {x for x in range(20, 39)}
    b = {(x, y) for x in range(100) for y in range(x, x + 5) if x % 39 in a}
    print(a)
    print(b)


if __name__ == '__main__':
    main()
