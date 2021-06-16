def main():
    a = [1, 2, 3]

    for index in range(4):
        try:
            print(a[index])
        except Exception:
            pass
        finally:
            print("Finished an iteration")

    for index in range(4):
        try:
            print(a[index])
        finally:
            print("Finished an iteration")


if __name__ == '__main__':
    main()
