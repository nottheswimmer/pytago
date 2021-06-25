def main():
    a = {1, 2, 3, 4}
    b = {4, 5, 6}
    b.add(7)
    print(a.union(b))
    print(a.intersection(b))
    print(a.difference(b))
    print(a.symmetric_difference(b))

    print(a.issubset(b))
    print(a.issuperset(b))


if __name__ == '__main__':
    main()
