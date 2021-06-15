def main():
    i = 0
    while True:
        print(i)
        i += 1
        if i > 5:
            break

    j = 10
    while j < 100:
        print(j)
        j += 10

    while 1:
        print(j + i)
        break

    while 0.1:
        print(j + i)
        break

    while 0:
        print("This never executes")

    while 0.0:
        print("This never executes")

    while None:
        print("This never executes")

    while False:
        print("This never executes")

    while "":
        print("This never executes")

    while "hi":
        print("This executes")
        break

if __name__ == '__main__':
    main()
