def main():
    a = [1, 2, 3]
    print(a[0])
    print(a[1])
    print(a[2])
    a.append(4)
    print(a[3])
    a += [5, 6, 7]
    a = a + [8, 9, 10]
    print(a[4])
    print(a[-1])

if __name__ == '__main__':
    main()
