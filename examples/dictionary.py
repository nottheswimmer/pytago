def main():
    a = {"name": "Michael", "age": 24, 1337: True}
    print(a)
    a["sleepiness"] = 1.0
    del a[1337]

    for k, v in a.items():
        print(k)
        print(v)

