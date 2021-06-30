import glob

def main():
    for py_file in glob.glob("./*.py"):
        print("=" * 20, py_file, "=" * 20)
        with open(py_file) as py_f:
            for line in py_f:
                print(line.rstrip())

if __name__ == '__main__':
    main()
