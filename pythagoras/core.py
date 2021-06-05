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
    a = 3
    b = 7
    a = a + b
    print(a + b)
    another_scope()


def another_scope():
    a = 1
    b = 12
    a = a + b
    print(a + b)


if __name__ == '__main__':
    main()
"""))
