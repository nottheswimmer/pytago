def main():
    stuff = [1, 5, "hello", 5, 12, 19, 12.5, [1, 2, 3]]
    write_contents(stuff)
    items = ["", 0, 1.1]
    for x in items:
        if isinstance(x, str):
            print("See? It's not used here so we don't have a type assertion")
        elif isinstance(x, int):
            print("This is very important because go's compiler will complain")
        else:
            print("You know, I wouldn't have to worry about this if we had something to remove unused initializations")

def write_contents(contents):
    with open("contents.txt", "w+") as f:
        for item in contents:
            if isinstance(item, str):
                f.write("str: " + item + "\n")
            elif isinstance(item, int):
                f.write("int: " + str(item) + "\n")
            else:
                f.write("unknown: " + repr(item) + "\n")


if __name__ == '__main__':
    main()
