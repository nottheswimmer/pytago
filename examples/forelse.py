def main():
    for x in range(4):
        if x == 5:
            break
    else:
        print("Well of course that didn't happen")

    for x in range(7):
        if x == 5:
            break
    else:
        print("H-hey wait!")

    i = 0
    while i < 3:
        print("Works with while too")
        for x in range(3):
            print("BTW don't worry about nested breaks")
            break
        if i == 10:
            break
        i += 1
    else:
        print("Yeah not likely")
    print(i)


if __name__ == '__main__':
    main()
