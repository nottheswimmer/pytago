import ast
from _ast import AST

from pythagoras.go_ast import CallExpr, Ident, SelectorExpr, File, FuncDecl, BinaryExpr, token, AssignStmt, BlockStmt, \
    CompositeLit, Field, Scope, Object, ObjKind, RangeStmt, ForStmt, BasicLit, IncDecStmt, UnaryExpr, IndexExpr, \
    GoBasicType, Stmt, IfStmt, ExprStmt, DeferStmt, FuncLit, FuncType, FieldList, ReturnStmt, ImportSpec, ArrayType


class PrintToFmtPrintln(ast.NodeTransformer):
    """
    This should probably add an import, but goimports takes care of that in postprocessing for now.
    """

    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node.Fun:
            case Ident(Name="print"):
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
            match decl:
                case FuncDecl(Name=Ident(Name="_")):
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
        match node:
            case SelectorExpr(X=Ident(Name="math"), Sel=Ident()):
                node.Sel.Name = node.Sel.Name.title()
        return node


class ReplacePowWithMathPow(ast.NodeTransformer):
    def visit_BinaryExpr(self, node: BinaryExpr):
        self.generic_visit(node)
        match node:
            case BinaryExpr(Op=token.PLACEHOLDER_POW):
                return CallExpr(Args=[node.X, node.Y],
                                Fun=SelectorExpr(X=Ident.from_str("math"), Sel=Ident.from_str("Pow")))
        return node


class ReplacePythonStyleAppends(ast.NodeTransformer):
    def visit_BlockStmt(self, block_node: BlockStmt):
        self.generic_visit(block_node)
        for i, node in enumerate(block_node.List):
            match node:
                case ExprStmt(X=CallExpr(Fun=SelectorExpr(Sel=Ident(Name="append")))):
                    block_node.List[i] = AssignStmt(
                        [node.X.Fun.X], [CallExpr(Args=[node.X.Fun.X, *node.X.Args], Fun=Ident.from_str("append"))],
                        token.ASSIGN)
        return block_node


class AppendSliceViaUnpacking(ast.NodeTransformer):
    def visit_AssignStmt(self, node: AssignStmt):
        self.generic_visit(node)
        match node:
            case AssignStmt(Rhs=[CompositeLit(), * ignored], Tok=token.ADD_ASSIGN):
                node.Rhs[0] = CallExpr(Args=[node.Lhs[0], node.Rhs[0]],
                                       Ellipsis=1, Fun=Ident.from_str("append"))
                node.Tok = token.ASSIGN
            case AssignStmt(Rhs=[BinaryExpr(Op=token.ADD, Y=CompositeLit()), * ignored]):
                node.Rhs[0] = CallExpr(Args=[node.Rhs[0].X, node.Rhs[0].Y],
                                       Ellipsis=1, Fun=Ident.from_str("append"))

        return node


class PythonToGoTypes(ast.NodeTransformer):
    def visit_Field(self, node: Field):
        self.generic_visit(node)
        match node.Type:
            case Ident(Name="str"):
                node.Type.Name = "string"
        return node


class NodeTransformerWithScope(ast.NodeTransformer):
    def __init__(self, scope=None):
        self.scope = Scope({}, scope)

    def generic_visit(self, node):
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, AST):
                        new_scope = isinstance(value, Stmt) and not isinstance(value, AssignStmt)
                        if new_scope:
                            self.scope = Scope({}, self.scope)
                        value = self.visit(value)
                        if new_scope:
                            self.scope = self.scope.Outer
                        if value is None:
                            continue
                        elif not isinstance(value, AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, AST):
                new_scope = isinstance(old_value, Stmt) and not isinstance(old_value, AssignStmt)
                if new_scope:
                    self.scope = Scope({}, self.scope)
                new_node = self.visit(old_value)
                if new_scope:
                    self.scope = self.scope.Outer
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def visit_AssignStmt(self, node: AssignStmt):
        """Don't forget to super call this if you override it"""
        eager_type_hint = next((self.scope._get_type(x) for x in node.Rhs), None)
        eager_context = {}
        for x in node.Rhs:
            eager_context.update(x._py_context)
        for expr in node.Lhs:
            if not expr._type_help:
                expr._type_help = eager_type_hint
            if eager_context:
                expr._py_context = {**eager_context, **expr._py_context}
        self.generic_visit(node)
        ctx = {}
        for x in node.Rhs:
            ctx.update(x._py_context)
        if node.Tok != token.DEFINE:
            return node
        declared = False
        for expr in node.Lhs:
            if not isinstance(expr, Ident):
                continue
            obj = Object(
                Data=None,
                Decl=None,
                Kind=ObjKind.Var,
                Name=expr.Name,
                Type=next((self.scope._get_type(x) for x in node.Rhs), None),
                _py_context=ctx
            )
            if not (self.scope._in_scope(obj) or self.scope._in_outer_scope(obj)):
                self.scope.Insert(obj)
                declared = True
        if not declared:
            node.Tok = token.ASSIGN
        return node


class RangeRangeToFor(ast.NodeTransformer):
    def visit_RangeStmt(self, node: RangeStmt):
        self.generic_visit(node)
        match node:
            case RangeStmt(X=CallExpr(Fun=Ident(Name="range"), Args=args)):
                match args:
                    case [stop]:
                        start, step = BasicLit(token.INT, 0), BasicLit(token.INT, 1)
                    case [start, stop]:
                        step = BasicLit(token.INT, 1)
                    case [start, stop, step]:
                        pass
                    case _:
                        return node
                init = AssignStmt(Lhs=[node.Value], Tok=token.DEFINE, Rhs=[start], TokPos=0)
                flipped = False
                match step:
                    case BasicLit(Value="1"):
                        post = IncDecStmt(Tok=token.INC, X=node.Value)
                    case UnaryExpr(Op=token.SUB, X=BasicLit(Value=val)):
                        if val == "1":
                            post = IncDecStmt(Tok=token.DEC, X=node.Value)
                        else:
                            post = AssignStmt(Lhs=[node.Value], Rhs=[step.X], Tok=token.SUB_ASSIGN)
                        flipped = True
                    case _:
                        post = AssignStmt(Lhs=[node.Value], Rhs=[step], Tok=token.ADD_ASSIGN)
                cond = BinaryExpr(X=node.Value, Op=token.GTR if flipped else token.LSS, Y=stop)
                return ForStmt(Body=node.Body, Cond=cond, Init=init, Post=post)
        return node


class UnpackRange(ast.NodeTransformer):
    def visit_RangeStmt(self, node: RangeStmt):
        self.generic_visit(node)
        match node:
            case RangeStmt(X=CallExpr(Fun=Ident(Name="enumerate"))):
                node.X = node.X.Args[0]
                node.Key = node.Value.Elts[0]
                node.Value = node.Value.Elts[1]
            case RangeStmt(X=CallExpr(Fun=SelectorExpr(Sel=Ident(Name="items")))):
                node.X = node.X.Fun.X
                node.Key = node.Value.Elts[0]
                node.Value = node.Value.Elts[1]
        return node


class NegativeIndexesSubtractFromLen(ast.NodeTransformer):
    """
    Will need some sort of type checking to ensure this doesn't affect maps or similar
    once map support is even a thing
    """

    def visit_IndexExpr(self, node: IndexExpr):
        self.generic_visit(node)
        match node.Index:
            case UnaryExpr(Op=token.SUB, X=BasicLit()):
                node.Index = BinaryExpr(X=CallExpr(Args=[node.X], Fun=Ident.from_str("len")),
                                        Op=token.SUB, Y=node.Index.X)
        return node


def wrap_with_call_to(args, wrap_with):
    if not isinstance(args, list):  # args must be an iterable but if it's not a list convert it to one
        args = list(args)
    if "." in wrap_with:
        x, sel = wrap_with.split(".")
        func = SelectorExpr(X=Ident.from_str(x), Sel=Ident.from_str(sel))
    else:
        func = Ident.from_str(wrap_with)
    return CallExpr(Args=args, Ellipsis=0, Fun=func, Lparen=0, Rparen=0)


class StringifyStringMember(NodeTransformerWithScope):
    """
    "Hello"[0] in Python is "H" but in Go it's a byte. Let's cast those back to string
    """

    def visit_IndexExpr(self, node: IndexExpr):
        self.generic_visit(node)
        if self.scope._get_type(node.X) == GoBasicType.STRING and self.scope._get_type(node.Index) == GoBasicType.INT:
            return wrap_with_call_to([node], GoBasicType.STRING.value)
        return node


class FileWritesAndErrors(NodeTransformerWithScope):
    def __init__(self):
        super().__init__()
        self.stack = []

    def generic_visit(self, node):
        self.stack.append(node)
        return_val = super().generic_visit(node)
        self.stack.pop()
        return return_val

    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node:
            case CallExpr(Fun=SelectorExpr(X=Ident(Name="os"), Sel=Ident(Name="OpenFile"))):
                f = Ident.from_str("f", _type_help=node._type(), _py_context=node._py_context)
                assignment = AssignStmt([f, Ident.from_str(UNHANDLED_ERROR)], [node], token.DEFINE)
                return CallExpr(Args=[], Fun=FuncLit(
                    Body=BlockStmt(
                        List=[
                            assignment,
                            ReturnStmt([f])
                        ],
                    ),
                    Type=FuncType(Results=FieldList(List=[Field(Type=node._type())]))
                ), _py_context=node._py_context)
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="write"))):
                n = Ident.from_str("n")
                selector = "WriteString" if self.scope._get_ctx(node.Fun.X)['text_mode'] else "Write"
                return CallExpr(Args=[], Fun=FuncLit(
                    Body=BlockStmt(
                        List=[
                            AssignStmt([n, Ident.from_str(UNHANDLED_ERROR)], [
                                CallExpr(Args=node.Args, Fun=node.Fun.X.sel(selector))
                            ], token.DEFINE),
                            ReturnStmt([n])
                        ],
                    ),
                    Type=FuncType(Results=FieldList(List=[Field(Type=Ident.from_str(GoBasicType.INT.value))]))
                ))
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="read"))):
                content = Ident.from_str("content")
                text_mode = self.scope._get_ctx(node.Fun.X)['text_mode']
                expr = CallExpr(Args=[], Fun=FuncLit(
                    Body=BlockStmt(
                        List=[
                            AssignStmt(Lhs=[content, Ident.from_str(UNHANDLED_ERROR)], Rhs=[
                                Ident.from_str("ioutil").sel("ReadAll").call(node.Fun.X)
                            ], Tok=token.DEFINE),
                            ReturnStmt(Results=[CallExpr(Fun=Ident.from_str(GoBasicType.STRING.value), Args=[content]) if text_mode else content])
                        ],
                    ),
                    Type=FuncType(Results=FieldList(List=[
                        Field(Type=Ident.from_str(GoBasicType.STRING.value) if text_mode else ArrayType.from_Ident(Ident.from_str(GoBasicType.BYTE.value)))]))
                ))
                return expr
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="decode"))):
                string = Ident.from_str(GoBasicType.STRING.value)
                return string.call(node.Fun.X)
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="encode"))):
                bytes_array = ArrayType(Elt=Ident.from_str(GoBasicType.BYTE.value))
                return bytes_array.call(node.Fun.X)
        return node


def _type_score(typ):
    return [
        "uint",
        "uintptr",
        "bool",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "int8",
        "int16",
        "int32",
        "int",
        "int64",
        "float32",
        "float64",
        "complex64",
        "complex128",
    ].index(str(typ).lower())


def get_dominant_type(type_a, type_b):
    # Pick a type to coerce things to
    return max((type_a, type_b), key=_type_score)


class HandleTypeCoercion(NodeTransformerWithScope):
    def visit_BinaryExpr(self, node: BinaryExpr):
        self.generic_visit(node)
        x_type, y_type = self.scope._get_type(node.X), self.scope._get_type(node.Y)
        match node.Op:
            case token.PLACEHOLDER_FLOOR_DIV:
                node.Op = token.QUO
                if x_type != GoBasicType.INT or y_type != GoBasicType.INT:
                    if x_type == GoBasicType.INT:
                        node.X = wrap_with_call_to([node.X], GoBasicType.FLOAT64.value)
                    if y_type == GoBasicType.INT:
                        node.Y = wrap_with_call_to([node.Y], GoBasicType.FLOAT64.value)
                    return wrap_with_call_to([node], "math.Floor")
            case token.QUO:
                if x_type == GoBasicType.INT:
                    node.X = wrap_with_call_to([node.X], GoBasicType.FLOAT64.value)
                    x_type = GoBasicType.FLOAT64
                if y_type == GoBasicType.INT:
                    node.Y = wrap_with_call_to([node.Y], GoBasicType.FLOAT64.value)
                    y_type = GoBasicType.FLOAT64
        if x_type != y_type and x_type and y_type:
            dominant_type = get_dominant_type(x_type, y_type)
            if x_type != dominant_type:
                node.X = wrap_with_call_to([node.X], dominant_type.value)
            if y_type != dominant_type:
                node.Y = wrap_with_call_to([node.Y], dominant_type.value)
        return node


class RequestsToHTTP(NodeTransformerWithScope):
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node.Fun:
            case SelectorExpr(X=Ident(Name="requests")):
                node.Fun.X.Name = "http"
                node.Fun.Sel.Name = node.Fun.Sel.Name.title()
        return node


UNHANDLED_ERROR = 'UNHANDLED_ERROR'
UNHANDLED_HTTP_ERROR = 'UNHANDLED_HTTP_ERROR'
UNHANDLED_ERRORS = [UNHANDLED_ERROR, UNHANDLED_HTTP_ERROR]

HTTP_RESPONSE_TYPE = "HTTP_RESPONSE_TYPE"


class HTTPErrors(NodeTransformerWithScope):
    def __init__(self):
        super().__init__()

    def visit_AssignStmt(self, node: AssignStmt):
        node = super().visit_AssignStmt(node)
        if len(node.Rhs) != 1:
            return node
        rhn = node.Rhs[0]
        if isinstance(rhn, CallExpr) and \
                isinstance(rhn.Fun, SelectorExpr) and \
                isinstance(rhn.Fun.X, Ident) and rhn.Fun.X.Name == "http":
            node.Lhs.append(Ident.from_str(UNHANDLED_HTTP_ERROR))
            self.scope.Objects[node.Lhs[0].Name].Type = HTTP_RESPONSE_TYPE
        return node

    def visit_SelectorExpr(self, node: SelectorExpr):
        if self.scope._get_type(node.X) == HTTP_RESPONSE_TYPE:
            match node.Sel.Name:
                case "text":
                    return CallExpr(Args=[], Fun=FuncLit(
                        Body=BlockStmt(
                            List=[
                                AssignStmt([Ident.from_str("body"), Ident.from_str(UNHANDLED_ERROR)], [
                                    _call_from_name("ioutil.ReadAll", [_selector_from_name(f"{node.X.Name}.Body")])
                                ], token.DEFINE),
                                ReturnStmt([wrap_with_call_to([Ident.from_str("body")], GoBasicType.STRING.value)])
                            ],
                        ),
                        Type=FuncType(Results=FieldList(List=[
                            Field(Type=Ident.from_str(GoBasicType.STRING.value))]))
                    ))
        return node


def _selector_from_name(name: str):
    parts = reversed(name.split("."))
    parts = [Ident.from_str(x) for x in parts]
    while len(parts) > 1:
        X, Sel = parts.pop(), parts.pop()
        parts.append(SelectorExpr(Sel=Sel, X=X))
    return parts[0]


def _call_from_name(name: str, args=tuple()):
    args = list(args)
    return CallExpr(Args=args, Fun=_selector_from_name(name),
                    Ellipsis=0, Rparen=0, Lparen=0)


class HandleUnhandledErrorsAndDefers(NodeTransformerWithScope):
    def visit_BlockStmt(self, block_node: BlockStmt):
        self.generic_visit(block_node)
        for i, node in enumerate(block_node.List.copy()):
            if not isinstance(node, AssignStmt):
                continue
            unhandled_error = False
            unhandled_defers = []
            for lhn in node.Lhs:
                if isinstance(lhn, Ident) and lhn.Name in UNHANDLED_ERRORS:
                    if lhn.Name == UNHANDLED_HTTP_ERROR:
                        unhandled_defers.append(_call_from_name(f"{node.Lhs[0].Name}.Body.Close"))
                    lhn.Name = "err"
                    unhandled_error = True
            pos = i
            if unhandled_error:
                pos += 1
                block_node.List.insert(pos,
                                       IfStmt(
                                           Body=BlockStmt(0, [
                                               ExprStmt(X=wrap_with_call_to([Ident.from_str("err")], "panic"))], 0),
                                           Cond=BinaryExpr(X=Ident.from_str("err"), Op=token.NEQ,
                                                           Y=Ident.from_str("nil"), OpPos=0),
                                           Else=None,
                                           If=0,
                                           Init=None,
                                       ))
            for j, deferred_call in enumerate(unhandled_defers):
                pos += 1
                block_node.List.insert(pos, DeferStmt(deferred_call, 0))

        return block_node


class AddTextTemplateImportForFStrings(ast.NodeTransformer):
    """
    Usually goimports makes these sorts of things unnecessary,
    but this one was getting confused with html/template sometimes
    """

    def __init__(self):
        self.visited_fstring = False

    def visit_File(self, node: File):
        self.generic_visit(node)
        if self.visited_fstring:
            node.add_import(ImportSpec(Path=BasicLit(token.STRING, "text/template")))
        return node

    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node:
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="New"), X=Ident(Name="template")), Args=[BasicLit(Value='"f"')]):
                self.visited_fstring = True
        return node


ALL_TRANSFORMS = [
    PrintToFmtPrintln,
    RemoveOrphanedFunctions,
    CapitalizeMathModuleCalls,
    ReplacePowWithMathPow,
    ReplacePythonStyleAppends,
    AppendSliceViaUnpacking,
    PythonToGoTypes,
    NodeTransformerWithScope,
    RangeRangeToFor,
    UnpackRange,
    NegativeIndexesSubtractFromLen,
    StringifyStringMember,
    HandleTypeCoercion,
    RequestsToHTTP,
    HTTPErrors,
    FileWritesAndErrors,
    HandleUnhandledErrorsAndDefers,
    AddTextTemplateImportForFStrings
]
