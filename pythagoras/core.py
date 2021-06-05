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
    a = True
    b = False
    print(a)
    print(b)
    print(a and b)
    print(a or b)
    print(not a)
    print(not b)
    print(a and not b)
    print(a or not b)
    

if __name__ == '__main__':
    main()
"""))
