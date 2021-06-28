def main():
    fh = open("file.txt")
    for line in fh:
        print(line)
    fh.close()

    with open("file2.txt") as fh2:
        for line in fh2:
            print(line)


if __name__ == '__main__':
    main()
