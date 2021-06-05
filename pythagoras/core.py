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
    a = "hello"
    b = "world"
    c = a + " " + b
    print(c)
    print(double_it(c))
    print(c[1])
    print(c[1:6])


def double_it(c: str) -> str:
    return c + c


if __name__ == '__main__':
    main()

"""))
