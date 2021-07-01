class A:
    a: str

    def __init__(self, val):
        self.a = val

    def __str__(self):
        return self.a


def main():
    val = A("ok")
    print(val)


if __name__ == '__main__':
    main()
