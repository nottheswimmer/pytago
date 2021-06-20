def main():
    a = ["a", 1, "5", 2.3, 1.2j]
    some_condition = True
    for x in a:
        # If it's all isinstance, we can use a type switch
        if isinstance(x, (str, float)):
            print("String or float!")
        elif isinstance(x, int):
            print("Integer!")
        else:
            print("Dunno!")
            print(":)")

        # If it's got mixed expressions, we will inline a switch for the isinstance expression
        if isinstance(x, str) and some_condition:
            print("String")
        elif isinstance(x, int):
            print("Integer!")
        else:
            print("Dunno!!")
            print(":O")


if __name__ == '__main__':
    main()
