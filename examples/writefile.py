def main():
    some_text = "Hello world"
    with open("hello_world.tmp", "w") as f:
        f.write(some_text)


if __name__ == '__main__':
    main()
