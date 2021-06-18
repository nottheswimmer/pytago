def main():
    a = [1, 2, 3]
    b = [1, 2, 3]
    print(a == b)  # True
    print(a != b)  # False
    print(a is a)  # True
    print(a is b)  # False
    print(a is not a)  # False
    print(a is not b)  # True

if __name__ == '__main__':
    main()
