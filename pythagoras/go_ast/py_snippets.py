import ast
import inspect
from collections import defaultdict
from typing import TYPE_CHECKING, Generic, TypeVar, Generator

if TYPE_CHECKING:
    from pythagoras import go_ast

BINDABLES: dict['Bindable', list] = defaultdict(list)
__InterfaceOf = Generic

class Bindable:
    def __init__(self, f: callable, name: str):
        self.f = f
        self.name = name

    @property
    def src(self):
        return inspect.getsource(self.f)

    @property
    def ast(self):
        node = ast.parse(self.src).body[0]
        node.decorator_list = []
        return node

    @property
    def sig(self):
        return inspect.signature(self.f)

    @classmethod
    def add(cls, name):
        def inner(f):
            BINDABLES[name].append(cls(f, name))
            return f

        return inner


    def bind(self, *args):
        # Raises TypeError on failure
        return self.sig.bind(*args)

    def bind_partial(self, *args):
        return self.sig.bind_partial(*args)

    def binded_ast(self, binding):
        root = self.ast

        class Transformer(ast.NodeTransformer):
            def visit_arg(self, node: ast.arg):
                if node.arg in binding.arguments:
                    return None
                return self.generic_visit(node)

            def visit_Name(self, node: ast.Name):
                self.generic_visit(node)
                return binding.arguments.get(node.id, node)

        binded = Transformer().visit(root)
        return binded

    def binded_go_ast(self, binding):
        from pythagoras.go_ast import FuncLit
        binded_ast = self.binded_ast(binding)
        funclit = FuncLit.from_FunctionDef(binded_ast)
        return funclit



@Bindable.add("zip")
def go_zip(a: list, b: list):
    for i, e in enumerate(a):
        if i >= len(b):
            break
        yield e, b[i]


def find_call_funclit(node: ast.Call) -> 'go_ast.FuncLit':
    match node:
        case ast.Call(func=ast.Name(id=x), args=args):
            for i, b in enumerate(BINDABLES[x].copy()):
                try:
                    binding = b.bind(*args)
                except TypeError as e:
                    continue

                # Removing and adding these back out of paranoia that, otherwise,
                # an argument with the name of what we're binding to could cause this
                # to infinitely recurse
                del BINDABLES[x][i]
                go_ast = b.binded_go_ast(binding)
                BINDABLES[x].insert(i, x)
                return go_ast

if __name__ == '__main__':
    node = ast.parse(
"""
zip([1, 2, 3], [4, 5, 6])
"""
    ).body[0].value
    print(find_call_funclit(node))
