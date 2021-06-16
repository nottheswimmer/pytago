def main():
    a = [1, 2, 3]
    for index in range(4):
        try:
            print(a[index])
            if index == 1:
                raise ValueError(index)
        except IndexError:
            print("That index was out of bounds")
        except (NotImplementedError, RuntimeError):
            print("This won't actually happen...")
        except Exception as e:
            print("Some other exception occurred")
            print(e)


if __name__ == '__main__':
    main()

