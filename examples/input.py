def main():
    print("Hi, what's your name?")
    name = input("Name: ")
    print("Hi", name, "how old are you?")
    age = int(input("Age: "))
    print("Describe yourself in one sentence:")
    description = input()
    print("So your name is", name, "and you are", age, "years old, and your description is", '"' + description + '"')


if __name__ == '__main__':
    main()
