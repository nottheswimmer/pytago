def main():
    n = 111
    gen = (n * 7 for x in range(10))
    if 777 in gen:
        print("Yes!")


if __name__ == '__main__':
    main()
