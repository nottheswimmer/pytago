class Custom1:
    def __init__(self):
        pass


class Custom2:
    def __init__(self, x):
        self.x = x


def main():
    b = False
    i = 12
    f = 4.2
    s = "bla bla"
    sb = b"bla bla"
    # sba = bytearray(b"bla bla")
    s1 = {1, 2, 3}
    s2 = {"a", "b", "c"}
    d1 = {"hi": 1}
    d2 = {"hi": "hi"}
    l1 = [1, 2, 3]
    l2 = ["a", "b", "c"]
    t1 = (1, 2, 3)
    t2 = (1, 2)
    c1 = Custom1()
    c2 = Custom2(1)
    c3 = Custom2(2)
    fx = lambda x: print(x)
    fxy = lambda x, y: print(x, y)

    print("type(b) =", type(b))
    print("type(i) =", type(i))
    print("type(f) =", type(f))
    print("type(s) =", type(s))
    print("type(sb) =", type(sb))
    # print("type(sba) =", type(sba))
    print("type(d1) =", type(d1))
    print("type(d2) =", type(d2))
    print("type(l1) =", type(l1))
    print("type(l2) =", type(l2))
    print("type(t1) =", type(t1))
    print("type(t2) =", type(t2))
    print("type(c1) =", type(c1))
    print("type(c2) =", type(c2))
    print("type(s1) =", type(s1))
    print("type(s2) =", type(s2))
    print("type(c3) =", type(c3))
    print("type(fx) =", type(fx))
    print("type(fxy) =", type(fxy))
    print("type(d1) == type(d2)?", type(d1) == type(d2))
    print("type(l1) == type(l2)?", type(l1) == type(l2))
    print("type(t1) == type(t2)?", type(t1) == type(t2))
    print("type(l1) == type(t1)?", type(l1) == type(t1))
    print("type(c1) == type(c2)?", type(c1) == type(c2))
    print("type(c2) == type(c3)?", type(c2) == type(c3))
    print("type(fx) == type(fxy)?", type(fx) == type(fxy))
    print("type(s) == str?", type(s) == str)
    print("type(sb) == bytes?", type(sb) == bytes)
    # print("type(sba) == bytearray?", type(sba) == bytearray)
    # print("type(sb) == type(sba)?", type(sb) == type(sba))
    print("type(i) == int?", type(i) == int)
    print("type(f) == float?", type(f) == float)
    print("type(l1) == list?", type(l1) == list)
    print("type(t1) == tuple?", type(t1) == tuple)
    print("type(s1) == type(s2)?", type(s1) == type(s2))
    # print("type(s1) == type(d1)?", type(s1) == type(d1))
    print("type(c1) == Custom1", type(c1) == Custom1)
    print("type(c2) == Custom2", type(c2) == Custom2)
    print("type(c2) == Custom1", type(c2) == Custom1)


if __name__ == '__main__':
    main()
