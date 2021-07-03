import ast


# Hack to stop astroid from using lazy objects which causes inconsistent failures when deepcopying
import warnings

import lazy_object_proxy
from lazy_object_proxy import Proxy
failed_to_deactivate = []

class NoProxy(Proxy):
    __slots__ = '__target__', '__factory__', '__deepcopy__'

    def __init__(self, *args, **kwargs):
        super(NoProxy, self).__init__(*args, **kwargs)
        try:
            self.__wrapped__   # Deactivate proxy if possible
            self.__deepcopy__ = getattr(self.__wrapped__, '__deepcopy__', None)
        except (AttributeError, TypeError, ImportError, KeyError):
            failed_to_deactivate.append(self)

lazy_object_proxy.Proxy = NoProxy

import astroid


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
    astroid_tree = astroid.parse(source, *args, **kwargs)

    class SimultaneousTreeVisitor(ast.NodeVisitor):
        def generic_visit(self, node1, node2):
            if hasattr(node1, "_fields"):
                try:
                    node2._fields = node1._fields
                except AttributeError:
                    return
                for _field in node1._fields:
                    if not hasattr(node2, _field):
                        setattr(node2, _field, getattr(node1, _field, None))
            for (field, value), (field2, value2) in zip(ast.iter_fields(node1), ast.iter_fields(node2)):
                if isinstance(value, list):
                    if not isinstance(value2, list):
                        value2 = [value2]
                    for item, item2 in zip(value, value2):
                        if isinstance(item, ast.AST):
                            self.visit(item, item2)
                elif isinstance(value, ast.AST):
                    self.visit(value, value2)

        def visit(self, node1, node2):
            """Visit a node."""
            method = 'visit_' + node1.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node1, node2)

        def visit_Constant(self, node1, node2):
            value = node1.value
            type_name = ast._const_node_type_names.get(type(value))
            if type_name is None:
                for cls, name in ast._const_node_type_names.items():
                    if isinstance(value, cls):
                        type_name = name
                        break
            if type_name is not None:
                method = 'visit_' + type_name
                try:
                    visitor = getattr(self, method)
                except AttributeError:
                    pass
                else:
                    import warnings
                    warnings.warn(f"{method} is deprecated; add visit_Constant",
                                  DeprecationWarning, 2)
                    return visitor(node1, node2)
            return self.generic_visit(node1, node2)

    class TreeLinker(SimultaneousTreeVisitor):
        def __init__(self, attr, fn = None):
            self.attr = attr
            self.fn = fn or (lambda x: x)

        def generic_visit(self, node1, node2):
            super().generic_visit(node1, node2)
            setattr(node1, self.attr, self.fn(node2))
            try:
                setattr(node2, self.attr, node1)
            except AttributeError:
                pass


    def build_linked_node(_node):
        allowed = ("locals", "_linked", "nodeclare", "__dict__", "_fields", "lineno", "col_offset",
                   *getattr(_node, "_fields", []))
        for attr in dir(_node):
            if attr not in allowed:
                try:
                    delattr(_node, attr)  # Objects not deepcopyable otherwise
                except (AttributeError, TypeError):
                    pass
        return _node


    TreeLinker('_linked', build_linked_node).visit(tree, astroid_tree)


    # Do our best to ensure nothing is left proxied by Astroid.
    if failed_to_deactivate:
        for i in range(10):
            failed_to_deactivate_still = []
            for failure in failed_to_deactivate:
                try:
                    failure.__wrapped__
                    failure.__deepcopy__ = getattr(failure.__wrapped__, '__deepcopy__', None)
                except Exception as e:
                    failed_to_deactivate_still.append(failure)
            if not failed_to_deactivate_still:
                break
            failed_to_deactivate[:] = failed_to_deactivate_still
        else:
            warnings.warn("Some proxies remain")
    return tree

# Debugging
if __name__ == '__main__':  # pragma: no cover
    print(python_to_go(r"""
ADMINS = ["Michael"]


class Player:
    name: str
    level: int
    health: int

    def __str__(self):
        return f"{self.name} (Level {self.level})"

    def __init__(self, name, level, health):
        self.name = name
        self.level = level
        self.health = health


def main():
    name = input("Welcome! What is your name?\n> ")
    if name in ADMINS:
        level = 999
        health = 10000
    else:
        level = 1
        health = 10

    player = Player(name, level, health)
    print("Welcome,", player)


if __name__ == '__main__':
    main()
"""))
