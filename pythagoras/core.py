import ast

from pythagoras import go_ast


def python_to_go(python: str) -> str:
    tree = ast.parse(python)
    go_code = go_ast.unparse(tree)
    return go_code


# Debugging
if __name__ == '__main__':
    print(python_to_go("""\
import math

def main():
    print(math.sin(3))
    print(math.cosh(3))
    print(math.pi)
    print(math.acosh(6))
    print(math.atan2(4, 7))

if __name__ == '__main__':
    main()

"""))
