import ast

from pythagoras.go_ast import CallExpr, Ident, SelectorExpr


class PrintToFmtPrintlnTransformer(ast.NodeTransformer):
    """
    This should probably add an import, but goimports takes care of that in postprocessing for now.
    """
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        if isinstance(node.Fun, Ident):
            if node.Fun.Name == "print":
                node.Fun = SelectorExpr(X=Ident.from_str("fmt"), Sel=Ident.from_str("Println"))
        return node

ALL_TRANSFORMS = [
    PrintToFmtPrintlnTransformer
]