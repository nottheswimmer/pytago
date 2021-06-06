import ast

from pythagoras import go_ast


def python_to_go(python: str) -> str:
    py_tree = ast.parse(python)
    go_tree = go_ast.File.from_Module(py_tree)
    return go_ast.unparse(go_tree)



# Debugging
if __name__ == '__main__':
    print(python_to_go("""\
def main():
    a = 7
    b = add(a, -2)
    if a > b:
        print("It's bigger")
    elif a == b:
        print("They're equal")
    else:
        print("It's smaller")


def add(a: int, b: int) -> int:
    return a + b


if __name__ == '__main__':
    main()
"""))
