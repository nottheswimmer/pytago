import ast

from pythagoras import go_ast


def python_to_go(python: str) -> str:
    tree = ast.parse(python)
    go_code = go_ast.unparse(tree)
    return go_code


# Debugging
if __name__ == '__main__':
    print(python_to_go("""\
import requests


def main():
    resp = requests.get("http://tour.golang.org/welcome/1")
    print(resp.text)

if __name__ == '__main__':
    main()
"""))
