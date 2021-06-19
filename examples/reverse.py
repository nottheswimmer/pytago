def main():
    a = [1, 2, 3, 4, 5]

    # Even though this is technically an iterator I'm going to let
    # go just copy it for the initial implementation since that's
    # probably what you'd do in go (or just reverse in-place -- .reverse() for that)
    for x in reversed(a):
        print(x)

    for x in a:
        print(x)

    a.reverse()

    for x in a:
        print(x)


if __name__ == '__main__':
    main()
