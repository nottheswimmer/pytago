import json
import random


def main():
    print(json.dumps(1))
    print(json.dumps("hello"))
    c = json.dumps({"hello": 1, "how": "are you"})
    print(c + c)
    print(json.dumps([1, 2, 3]))


if __name__ == '__main__':
    main()
