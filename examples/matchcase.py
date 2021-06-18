def main():
    a = 1
    match a:
        case 1:
            print(1)
        case 2:
            print(2)
        case 3:
            print(3)

    match a:
        case 4:
            print("Never gonna happen")
        case _:
            print("Nice, defaults!")


if __name__ == '__main__':
    main()
