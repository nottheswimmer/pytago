def main():
    a = {(x, y): x*y for x in range(20) for y in range(5) if x*y != 0}
    for k, v in a.items():
        print(k, v)


if __name__ == '__main__':
    main()
