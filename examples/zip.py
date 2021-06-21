def main():
    x = [1, 2, 3]
    y = [4, 5, 6]
    zipped = zip(x, y)
    for pair in zipped:
        print(pair)

if __name__ == '__main__':
    main()
