def main():
    # Iterables should compare the index of the element to -1
    a = [1, 2, 3]
    print(1 in a)
    print(4 in a)
    print(5 not in a)

    # Strings should either use strings.Compare or use strings.Index with a comparison to -1
    # While the former is more straight forward, I think the latter will be nicer for consistency
    b = "hello world"
    print("hello" in b)
    print("Hello" not in b)

    # Checking for membership in a dictionary means we need to check if the key is in it
    # ... Eventually this should behave well with mixed types
    c = {"hello": 1, "world": 2}
    print("hello" in c)
    print("Hello" not in c)

    # Bytes
    d = b'hello world'
    print(b'hello' in d)
    print(b'Hello' not in d)

    # Sets
    e = {1, 2, 3, "hello"}
    print("hello" in e)
    print(4 not in e)

if __name__ == '__main__':
    main()
