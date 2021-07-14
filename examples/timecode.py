import time


def main():
    print(time.time())
    print(time.time_ns())
    print(time.ctime(time.time()))
    print(time.ctime(1000000000))


if __name__ == '__main__':
    main()
