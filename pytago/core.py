import ast


def python_to_go(python: str, debug=True) -> str:
    from pytago import go_ast
    py_tree = build_source_tree(python)
    go_tree = go_ast.File.from_Module(py_tree)
    return go_ast.unparse(go_tree, debug=debug)


def dump_python_to_go_ast_as_json(python: str):  # pragma: no cover
    from pytago import go_ast
    """
    Not currently used for anything. Hoping that this could
    be the first step toward serializing ASTs to send to
    a go program directly
    """
    py_tree = build_source_tree(python)
    go_tree = go_ast.File.from_Module(py_tree)
    from pytago.go_ast import clean_go_tree
    clean_go_tree(go_tree)
    return go_ast.dump_json(go_tree)


def build_source_tree(source, *args, **kwargs) -> ast.Module:
    tree = ast.parse(source, *args, **kwargs)

    # class MakeTreeBiDirectional(ast.NodeVisitor):
    #     def generic_visit(self, node):
    #         for field, value in ast.iter_fields(node):
    #             if isinstance(value, list):
    #                 for item in value:
    #                     if isinstance(item, ast.AST):
    #                         self.visit(item)
    #                         item.parent = node
    #             elif isinstance(value, ast.AST):
    #                 self.visit(value)
    #                 value.parent = node
    #
    # MakeTreeBiDirectional().visit(tree)

    return tree

# Debugging
if __name__ == '__main__':  # pragma: no cover
    print(dump_python_to_go_ast_as_json("""\
[(a, c) for a, *b, c in [] if b]
"""))
