def main():
    f = lambda x: x * 2
    for a in range(10):
        print((lambda x: x + 1)(a) + f(a))

if __name__ == '__main__':
    main()
