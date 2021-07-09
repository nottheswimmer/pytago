class Number:
    def __init__(self, x):
        self.x = x

    def __add__(self, other: 'Number'):
        return Number(self.x + other.x)

    def __mul__(self, other: 'Number'):
        return Number(self.x * other.x)

    def __str__(self):
        return str(self.x)


class ComplexNumber:
    def __init__(self, real, imag):
        self.real = real
        self.imag = imag

#    def __add__(self, other: 'ComplexNumber'):
#        return ComplexNumber(self.real + other.real, self.imag + other.imag)

    def __str__(self):
        return str(self.real) + "+" + str(self.imag) + "i"


def main():
    five = Number(5)
    six = Number(6)
    eleven = five + six
    print(eleven)
    fifty_five = eleven * five
    print(fifty_five)
    i = ComplexNumber(Number(0), Number(-1))
    n = ComplexNumber(Number(3), Number(-6))
    # print(i + n)
    print(i, n)


if __name__ == '__main__':
    main()
