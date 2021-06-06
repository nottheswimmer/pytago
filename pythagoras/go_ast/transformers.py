import ast

from pythagoras.go_ast import CallExpr, Ident, SelectorExpr, File, FuncDecl, BinaryExpr, token, AssignStmt, BlockStmt, \
    CompositeLit, Field, Scope, Object, ObjKind


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


class CapitalizeMathModuleCalls(ast.NodeTransformer):
    """
    The math module in Go is extremely similar to Python's, save for some capitalization difference
    """
    def visit_SelectorExpr(self, node: SelectorExpr):
        self.generic_visit(node)
        if isinstance(node.X, Ident) and node.X.Name == "math" and isinstance(node.Sel, Ident):
            node.Sel.Name = node.Sel.Name.title()
        return node


class ReplacePowWithMathPow(ast.NodeTransformer):
    def visit_BinaryExpr(self, node: BinaryExpr):
        self.generic_visit(node)
        if node.Op == token.PLACEHOLDER_POW:
            return CallExpr([node.X, node.Y], 0, SelectorExpr(X=Ident.from_str("math"), Sel=Ident.from_str("Pow")), 0, 0)
        return node


class ReplacePythonStyleAppends(ast.NodeTransformer):
    def visit_BlockStmt(self, block_node: BlockStmt):
        self.generic_visit(block_node)
        for i, node in enumerate(block_node.List):
            try:
                is_append = node.X.Fun.Sel.Name == "append"
            except AttributeError:
                is_append = False
            if not is_append:
                continue
            block_node.List[i] = AssignStmt([node.X.Fun.X],
                                            [CallExpr([node.X.Fun.X, *node.X.Args], 0, Ident.from_str("append"), 0, 0)],
                                            token.ASSIGN, 0)
        return block_node

class AppendSliceViaUnpacking(ast.NodeTransformer):
    def visit_AssignStmt(self, node: AssignStmt):
        self.generic_visit(node)
        try:
            aug_assign_composite = isinstance(node.Rhs[0], CompositeLit) and node.Tok == token.ADD_ASSIGN
        except (IndexError, AttributeError):
            aug_assign_composite = False
        if aug_assign_composite:
            node.Rhs[0] = CallExpr(Args=[node.Lhs[0], node.Rhs[0]],
                                 Ellipsis=1, Fun=Ident.from_str("append"),
                                 Lparen=0, Rparen=0)
            node.Tok = token.ASSIGN
            return node
        try:
            assign_composite = node.Rhs[0].Op == token.ADD and isinstance(node.Rhs[0].Y, CompositeLit)
        except (IndexError, AttributeError):
            assign_composite = False
        if assign_composite:
            node.Rhs[0] = CallExpr(Args=[node.Rhs[0].X, node.Rhs[0].Y],
                                 Ellipsis=1, Fun=Ident.from_str("append"),
                                 Lparen=0, Rparen=0)

            return node
        return node


class PythonToGoTypes(ast.NodeTransformer):
    def visit_Field(self, node: Field):
        self.generic_visit(node)
        if isinstance(node.Type, Ident):
            if node.Type.Name == "str":
                node.Type.Name = "string"
        return node

class PreventRepeatDeclarations(ast.NodeTransformer):
    def __init__(self):
        self.scope = Scope({}, None)

    def visit_BlockStmt(self, node: BlockStmt):
        self.scope = Scope({}, self.scope)
        self.generic_visit(node)
        self.scope = self.scope.Outer
        return node

    def visit_AssignStmt(self, node: AssignStmt):
        self.generic_visit(node)
        if node.Tok != token.DEFINE:
            return node
        declared = False
        for expr in node.Lhs:
            if isinstance(expr, Ident):
                obj = Object(
                        Data=node.Rhs,
                        Decl=None,
                        Kind=ObjKind.Var,
                        Name=expr.Name,
                        Type=None,
                )
                if not (self.scope._in_scope(obj) or self.scope._in_outer_scope(obj)):
                    self.scope.Insert(obj)
                    declared = True
        if not declared:
            node.Tok = token.ASSIGN
        return node


ALL_TRANSFORMS = [
    PrintToFmtPrintln,
    RemoveOrphanedFunctions,
    CapitalizeMathModuleCalls,
    ReplacePowWithMathPow,
    ReplacePythonStyleAppends,
    AppendSliceViaUnpacking,
    PythonToGoTypes,
PreventRepeatDeclarations
]
