def main():
    with open("file_1.tmp", "w+") as f:
        f.write("This file was created in w+ mode\n")

    with open("file_2.tmp", "x") as f:
        f.write("This file was created by x mode\n")

    with open("file_2.tmp", "w") as f:
        f.write("This file was created by x mode and then overwritten in w mode\n")

    with open("file_2.tmp", "a") as f:
        f.write("... And then appended to in a mode\n")

    with open("file_2.tmp", "r") as f:
        print(f.read())

    with open("file_3.tmp", "a+") as f:
        f.write("This file was created in a+ mode\n")

    with open("file_4.tmp", "x+") as f:
        f.write("This file was created by x+ mode\n")

    with open("file_5.tmp", "wb+") as f:
        f.write(b"This file was created in wb+ mode\n")

    with open("file_6.tmp", "xb") as f:
        f.write(b"This file was created by xb mode\n")

    with open("file_6.tmp", "wb") as f:
        f.write(b"This file was created by xb mode and then overwritten in wb mode\n")

    with open("file_6.tmp", "ab") as f:
        f.write(b"... And then appended to in ab mode\n")

    with open("file_6.tmp", "rb") as f:
        print(f.read().decode())

    with open("file_7.tmp", "ab+") as f:
        f.write(b"This file was created in ab+ mode\n")

    with open("file_8.tmp", "xb+") as f:
        f.write(b"This file was created by xb+ mode\n")

    # with open("file_4.tmp", "x+") as f:
    #     pass

if __name__ == '__main__':
    main()
