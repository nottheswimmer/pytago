def main():
    for i in range(10):
        if i < 3 or i > 7:
            continue
        print(i)

if __name__ == '__main__':
    main()
