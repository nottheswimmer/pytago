def main():
    a = ((x, y) for x in range(5) for y in range(x))
    b = (w for w in ("Where", "Are", "You?", "And", "I'm", "So", "Sorry"))
    for l in b:
        print(l, next(a))
    for rest in a:
        print(rest)


if __name__ == '__main__':
    main()
