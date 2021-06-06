import ast

from pythagoras.go_ast import CallExpr, Ident, SelectorExpr, File, FuncDecl


class PrintToFmtPrintln(ast.NodeTransformer):
    """
    This should probably add an import, but goimports takes care of that in postprocessing for now.
    """
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        if isinstance(node.Fun, Ident):
            if node.Fun.Name == "print":
                node.Fun = SelectorExpr(X=Ident.from_str("fmt"), Sel=Ident.from_str("Println"))
        return node


class RemoveOrphanedFunctions(ast.NodeTransformer):
    """
    Orphaned code is placed in functions titled "_" -- later we may want to try to put such code in the main
    method or elsewhere, but for now we'll remove it.
    """
    def visit_File(self, node: File):
        self.generic_visit(node)
        to_delete = []
        for decl in node.Decls:
            if isinstance(decl, FuncDecl) and decl.Name.Name == '_':
                to_delete.append(decl)
        for decl in to_delete:
            node.Decls.remove(decl)
        return node


ALL_TRANSFORMS = [
    PrintToFmtPrintln,
    RemoveOrphanedFunctions
]
