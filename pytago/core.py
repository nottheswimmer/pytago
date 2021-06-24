import ast


def python_to_go(python: str, debug=True) -> str:
    from pytago import go_ast
    py_tree = ast.parse(python)
    go_tree = go_ast.File.from_Module(py_tree)
    return go_ast.unparse(go_tree, debug=debug)


def dump_python_to_go_ast_as_json(python: str):
    from pytago import go_ast
    """
    Not currently used for anything. Hoping that this could
    be the first step toward serializing ASTs to send to
    a go program directly
    """
    py_tree = ast.parse(python)
    go_tree = go_ast.File.from_Module(py_tree)
    from pytago.go_ast import clean_go_tree
    clean_go_tree(go_tree)
    return go_ast.dump_json(go_tree)


# Debugging
if __name__ == '__main__':
    print(dump_python_to_go_ast_as_json("""\
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
