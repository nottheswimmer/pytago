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
    a = 7
    b = 3
    c = 4.5
    print(a / b)
    print(a // b)
    print(a / c)
    print(a // c)
    print(a + b)
    print(a + c)


if __name__ == '__main__':
    main()

"""))
