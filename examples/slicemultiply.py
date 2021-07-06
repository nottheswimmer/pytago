def main():
    n = 3
    x = [1, 2, 3] * n
    x = x * 3
    x *= 3
    print(len(x), x)


if __name__ == '__main__':
    main()
