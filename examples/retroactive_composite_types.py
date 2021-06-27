def main():
    a = []
    a.append(3)

    b = []
    b += a

    c = {}
    c["hello"] = 1

    d = {}
    d[1] = 2
    d["gonna_be_an_interface"] = "yup"

    e = set()
    e.add(1)

    f = [[]]
    f[0].append(1)

    g = {}
    g[(1, 2)] = 3

    h = []
    h.append(1)
    h.append("hi")

    i = {}
    i[1] = "lol"
    i["2"] = "lmao"

    print(a, b, c, d, e, f, g, h)


if __name__ == '__main__':
    main()
