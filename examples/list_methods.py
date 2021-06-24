def main():
    l1 = [1]
    l2 = ["hello", "how", "are", "you?"]
    l3 = [6.2, 1.6, 1.2, 20.1]

    l1.append(2)
    print(l1)

    l1.extend([4, 5])
    print(l1)

    l1.insert(3, 3)
    print(l1)

    print(l1.index(2))

    print(l1.count(3))

    l1.remove(3)
    print(l1)

    while l1:
        print(l1.pop())

    l3.clear()
    print(l3)

    l1.sort()
    print(l1)
    l2.sort()
    print(l2)
    l3.sort()
    print(l3)
    l3.sort(reverse=True)
    print(l3)

    l2.reverse()
    print(l2)

    l4 = l2.copy()
    l4.pop()
    print(l4)
    print(l2)

if __name__ == '__main__':
    main()
