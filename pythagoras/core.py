import ast

from pythagoras import go_ast


def python_to_go(python: str) -> str:
    tree = ast.parse(python)
    go_code = go_ast.unparse(tree)
    return go_code


# Debugging
if __name__ == '__main__':
    print(python_to_go("""\
def main():
    a = [1, 2, 3]
    print(a[0])
    print(a[1])
    print(a[2])
    a.append(4)
    print(a[3])
    a += [5, 6, 7]
    print(a[4])
    print(a[-1])

if __name__ == '__main__':
    main()
"""))
