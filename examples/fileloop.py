def main():
    fh = open("file.txt")
    for line in fh:
        print(line)
    fh.close()

    with open("file2.txt") as fh2:
        for line in fh2:
            print(line)

    with open("file3.txt") as fh3:
        for l in fh3:
            print(l)


if __name__ == '__main__':
    main()
