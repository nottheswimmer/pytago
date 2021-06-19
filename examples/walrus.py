def main():
    if (a := some_func()) == 7:
        print(a)

    for x in (y := [1, 2, 3]):
        print(y)
        print(x)

    match j := 5:
        case 5:
            print(j)

    while (t1 := thing_1()) < 5 and (t2 := thing_2()) == 3:
        print(t1)
        print(t2)


def some_func():
    return 7


call_count = 0


def thing_1():
    global call_count
    call_count += 1
    return call_count


def thing_2():
    return 3


if __name__ == '__main__':
    main()
