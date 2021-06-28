import ast
import warnings
from _ast import AST
from typing import Optional

from pytago.go_ast import CallExpr, Ident, SelectorExpr, File, FuncDecl, BinaryExpr, token, AssignStmt, BlockStmt, \
    CompositeLit, Field, Scope, Object, ObjKind, RangeStmt, ForStmt, BasicLit, IncDecStmt, UnaryExpr, IndexExpr, \
    GoBasicType, Stmt, IfStmt, ExprStmt, DeferStmt, FuncLit, FuncType, FieldList, ReturnStmt, ImportSpec, ArrayType, \
    ast_snippets, MapType, ValueSpec, Expr, BadStmt, SendStmt, len_
# Shortcuts
from pytago.go_ast.core import _find_nodes, GoAST, ChanType, StructType, InterfaceType, BadExpr, OP_COMPLIMENTS, \
    GoStmt, TypeSwitchStmt, StarExpr, GenDecl, CaseClause, SwitchStmt, TypeAssertExpr

v = Ident.from_str


class InterfaceTypeCounter(ast.NodeVisitor):
    def __init__(self):
        self.interface_types = 0
        
    def visit_InterfaceType(self, node: ast.NodeVisitor):
        self.interface_types += 1

    @classmethod
    def get_interface_count(cls, node: GoAST) -> int:
        counter = cls()
        counter.visit(node)
        return counter.interface_types


class BaseTransformer(ast.NodeTransformer):
    REPEATABLE = True
    STAGE = 1

    def __init__(self):
        self.exit_callbacks = [self.generic_exit_callback]
        self.at_root = True


    def visit(self, node: GoAST):
        at_root = self.at_root
        self.at_root = False
        # Perform the entire visiting process
        node = super().visit(node)
        if at_root:
            for callback in self.exit_callbacks:
                callback(node)
        return node

    def generic_exit_callback(self, *args, **kwargs):
        return

class ApplyPytagoInlines(BaseTransformer):
    STAGE = 0

    def __init__(self):
        super().__init__()
        self.to_inline = []

    def visit_AssignStmt(self, node: AssignStmt):
        # Handles PYTAGO_INLINE for statements/funclits
        match node.Lhs, node.Rhs:
            case [Ident(Name="PYTAGO_INLINE")], [x]:
                node.Lhs.pop()
                self.generic_visit(node)
                self.to_inline.append(x)
                return
        node = self.generic_visit(node)
        return node

    def visit_Ident(self, node: Ident):
        match node:
            case Ident(Name="PYTAGO_INLINE"):
                if self.to_inline:
                    return self.to_inline.pop()
        return node

class InsertUniqueInitializers(BaseTransformer):
    STAGE = 0
    REPEATABLE = False

    def __init__(self):
        super().__init__()
        self.to_initialize = []

    def visit_FuncLit(self, node: FuncLit):
        # Handles PYTAGO_INIT for expressions
        match node:
            case FuncLit(Body=BlockStmt(List=[AssignStmt(Lhs=[Ident(Name="PYTAGO_INIT")], Rhs=[x])])):
                if x not in self.to_initialize:
                    self.to_initialize.append(x)
                return
        return self.generic_visit(node)

    def visit_AssignStmt(self, node: AssignStmt):
        # Handles PYTAGO_INIT for statements/funclits
        match node.Lhs, node.Rhs:
            case [Ident(Name="PYTAGO_INIT")], [x]:
                if x not in self.to_initialize:
                    self.to_initialize.append(x)
                return
        return self.generic_visit(node)

    def generic_exit_callback(self, node: File, *args, **kwargs):
        for init in self.to_initialize:
            node.Decls.insert(1, FuncDecl(Body=init.Body, Type=init.Type, Name=Ident("init")))

    # TODO: PYTAGO_INIT for nonexpressions --
    #  possibly in a second transformer that takes place after the above
    # def visit_AssignStmt(self, node: AssignStmt):
    #     self.generic_visit(node)
    #     return node

class PrintToFmtPrintln(BaseTransformer):
    """
    This should probably add an import, but goimports takes care of that in postprocessing for now.
    """

    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node.Fun:
            case Ident(Name="print"):
                node.Fun = SelectorExpr(X=v("fmt"), Sel=v("Println"))
        return node


class RemoveIfNameEqualsMain(BaseTransformer):
    STAGE = 2
    REPEATABLE = False

    # TODO: in the future we want to support adding stuff from under
    #   "if __name__ == "__main__" to the main function
    #  Really, it should become the main function unless there already is one
    #  and it's calling it...

    def visit_FuncDecl(self, node: FuncDecl):
        match node.Name:
            case Ident(Name="init"):
                match node.Body:
                    case BlockStmt(List=[IfStmt(Cond=cond)]):
                        match cond:
                            case BinaryExpr(X=Ident(Name="__name__"), Op=token.EQL, Y=BasicLit(Value='"__main__"')) | \
                                BinaryExpr(X=Ident(Name="__main__"), Op=token.EQL, Y=BasicLit(Value='"__name__"')):
                                return
        return node


class CapitalizeMathModuleCalls(BaseTransformer):
    """
    The math module in Go is extremely similar to Python's, save for some capitalization difference
    """

    def visit_SelectorExpr(self, node: SelectorExpr):
        self.generic_visit(node)
        match node:
            case SelectorExpr(X=Ident(Name="math"), Sel=Ident()):
                if node.Sel.Name.islower():
                    node.Sel.Name = node.Sel.Name.title()
        return node


class ReplacePythonStyleAppends(BaseTransformer):
    def visit_BlockStmt(self, block_node: BlockStmt):
        self.generic_visit(block_node)
        for i, node in enumerate(block_node.List):
            match node:
                case ExprStmt(X=CallExpr(Fun=SelectorExpr(Sel=Ident(Name="append")))):
                    block_node.List[i] = AssignStmt(
                        [node.X.Fun.X], [CallExpr(Args=[node.X.Fun.X, *node.X.Args], Fun=v("append"))],
                        token.ASSIGN)
        return block_node



class PythonToGoTypes(BaseTransformer):
    def visit_Field(self, node: Field):
        self.generic_visit(node)
        match node.Type:
            case Ident(Name="str"):
                node.Type.Name = "string"
        return node


def compatible_types(type_1: AST, type_2: AST):
    if isinstance(type_1, InterfaceType) or isinstance(type_2, InterfaceType):
        return True
    if isinstance(type_1, MapType) and isinstance(type_2, MapType):
        return compatible_types(type_1.Key, type_2.Key) and compatible_types(type_1.Value, type_2.Value)
    if isinstance(type_1, ArrayType) and isinstance(type_2, ArrayType):
        return compatible_types(type_1.Elt, type_2.Elt)
    return type_1 == type_2


class NodeTransformerWithScope(BaseTransformer):
    def __init__(self, scope=None):
        super().__init__()
        self.scope = Scope({}, scope)
        self.stack = []
        self.current_globals = []
        self.current_nonlocals = []
        self.missing_type_info = []

    def should_apply_new_scope(self, value):
        match value:
            case FuncDecl(Name="init"):
                return False
            case BlockStmt(parents=[FuncDecl(Name="init")]):
                return False
            case FuncLit():
                return True
        return isinstance(value, Stmt) and not isinstance(value, (AssignStmt, ValueSpec))

    def generic_visit(self, node):
        self.stack.append(node)
        prev_globals = self.current_globals
        prev_nonlocals = self.current_nonlocals

        if isinstance(node, (FuncDecl, FuncLit)):
            self.current_globals = []
            self.current_nonlocals = []

        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    # Handle globals
                    if isinstance(value, BadStmt):
                        match value._pyAST:
                            case ast.Global(names=names):
                                self.current_globals += names
                            case ast.Nonlocal(names=names):
                                self.current_nonlocals += names
                    if isinstance(value, AST):
                        new_scope = self.should_apply_new_scope(value)
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
                new_scope = self.should_apply_new_scope(old_value)
                if new_scope:
                    self.scope = Scope({}, self.scope)
                new_node = self.visit(old_value)
                if new_scope:
                    self.scope = self.scope.Outer
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)

        self.current_globals = prev_globals
        self.current_nonlocals = prev_nonlocals
        self.stack.pop()

        if len(self.stack) == 0:
            # Deal with stuff that was missing
            resolved_objs = []
            for i, mti in enumerate(self.missing_type_info):
                expr, val, scope, callbacks = mti
                resolved = False
                t = None
                match val:
                    case CallExpr():
                        t = scope._get_type(val.Fun)
                        match t:
                            case FuncType(Results=FieldList(List=[Field(Type=x)])):
                                expr._type_help = x
                                resolved = True
                            case _:
                                expr._type_help = t
                                resolved = True
                if resolved:
                    if mti not in resolved_objs:
                        resolved_objs.append(mti)
                    while callbacks:
                        callbacks.pop()(expr, val, t)
            for obj in resolved_objs:
                try:
                    self.missing_type_info.remove(obj)
                except ValueError:
                    pass

        return node

    def visit_ValueSpec(self, node: ValueSpec):
        self.apply_eager_context(node.Names, node.Values)
        self.generic_visit(node)
        self.apply_to_scope(node.Names, node.Values)
        return node

    def visit_FuncDecl(self, node: FuncDecl):
        return self.visit_FuncDecl_or_FuncLit(node)

    def visit_FuncLit(self, node: FuncLit):
        return self.visit_FuncDecl_or_FuncLit(node)

    def visit_FuncDecl_or_FuncLit(self, node: FuncDecl | FuncLit):
        names = []
        values = []
        func_name = None
        if isinstance(node, FuncLit):
            if self.stack and isinstance(self.stack[-1], AssignStmt):
                match self.stack[-1].Lhs:
                    case [Ident(Name=name) as idnt]:
                        pass
                        # if isinstance(name, str):
                        #     func_name = idnt  # lambdas
                        # else:
                        #     func_name = name
        else:
            func_name = node.Name
        if func_name:
            names.append(func_name)
            values.append(node.Type)
        if node.Type.Params:
            for p in node.Type.Params.List:
                names += p.Names
                values += [p.Type] * len(p.Names)
        if node.Type.Results:
            result_names = []
            result_vals = []
            for p in node.Type.Results.List:
                result_names += p.Names
                result_vals += [p.Type] * len(p.Names)
            if result_names and result_vals:
                self.apply_eager_context(result_names, result_vals, rhs_is_types=True, force_current=True)
                self.apply_to_scope(result_names, result_vals, rhs_is_types=True, force_current=True)
        self.apply_eager_context(names, values, rhs_is_types=True)
        self.apply_to_scope(names, values, rhs_is_types=True)
        self.generic_visit(node)

        # Infer return type
        # TODO: clean up this rat's nest
        if node.Type.Results is None:
            def finder(x: GoAST):
                match x:
                    case ReturnStmt():
                        return x
                    case SendStmt(Chan=Ident(Name=name)):
                        return x if name == 'yield' else None
                return None

            stmts = _find_nodes(
                node.Body,
                finder=finder,
                skipper=lambda x: isinstance(x, FuncLit)
            )

            try:
                is_go = isinstance(self.stack[-1], CallExpr) and isinstance(self.stack[-2], GoStmt)
            except IndexError:
                is_go = False

            yielded = []
            if stmts:
                is_yield = False
                for stmt in stmts:
                    match stmt:
                        case ReturnStmt():
                            stmt: ReturnStmt
                            types = [self.scope._get_type(x) for x in stmt.Results]
                        case SendStmt():
                            stmt: SendStmt
                            types = [self.scope._get_type(stmt.Value)]
                            yielded.append(stmt.Value)
                        case _:
                            types = [None]

                    # if all(types) and (func_name or not is_yield or (node.Type.Results is None and not is_go)):
                    if all(types) and not (is_yield and is_go):
                        node.Type.Results = FieldList(List=[Field(Type=t) for t in types])
                        if func_name:
                            self.apply_to_scope([func_name], [node.Type])
                        break
                else:
                    if yielded and not is_go and node.Type.Results == None:
                        t = next((y for x in yielded if (y := x._type(interface_ok=True))), None)
                        node.Type.Results = FieldList(List=[Field(Type=t)])

                node._is_yield = is_yield

        return node

    def visit_RangeStmt(self, node: RangeStmt):
        lhs = []
        rhs = []
        rhs_is_types = True
        x_type = self.scope._get_type(node.X)
        match x_type:
            case MapType(Key=key_type, Value=val_type):
                if node.Key != Ident("_"):
                    lhs.append(node.Key)
                    rhs.append(key_type)
                if node.Value and node.Value != Ident("_"):
                    lhs.append(node.Value)
                    rhs.append(val_type)
            case ArrayType(Elt=elt_type):
                if node.Key != Ident("_"):
                    lhs.append(node.Key)
                    rhs.append(GoBasicType.INT.ident)
                if node.Value and node.Value != Ident("_"):
                    lhs.append(node.Value)
                    rhs.append(elt_type)
            case _:
                if node.Key != Ident("_"):
                    lhs.append(node.Key)
                if node.Value and node.Value != ("_"):
                    lhs.append(node.Value)
                if lhs:
                    rhs.append(node.X)
                rhs_is_types = False
        self.apply_eager_context(lhs, rhs, rhs_is_types=rhs_is_types)
        node = self.generic_visit(node)
        self.apply_to_scope(lhs, rhs, rhs_is_types=rhs_is_types)
        return node

    def visit_AssignStmt(self, node: AssignStmt):
        """Don't forget to super call this if you override it"""
        # Handle unpacking when both sides have multiple elements
        # TODO: Handle when lhs has multiple elements and rhs has one.
        match node:
            case AssignStmt(Lhs=[CompositeLit(Elts=lhs)], Rhs=[CompositeLit(Elts=rhs)]):
                node.Lhs = lhs
                node.Rhs = rhs
        self.apply_eager_context(node.Lhs, node.Rhs)
        self.generic_visit(node)
        if node.Tok != token.DEFINE:
            if all(self.scope._in_scope(x) or self.scope._in_outer_scope(x) for x in node.Lhs if isinstance(x, Ident)):
                # Tacking on some code to help NodeTransformerWithInterfaceTypes here
                if len(node.Lhs) == len(node.Rhs):
                    for l, r in zip(node.Lhs, node.Rhs):
                        l_type = self.scope._get_type(l)
                        r_type = self.scope._get_type(r)
                        if l_type != r_type:
                            match l_type, r_type:
                                case InterfaceType(), *anything:
                                    l_type._py_context.setdefault("elts", []).append(r)
                                case ArrayType(Elt=InterfaceType()), ArrayType(Elt=r_elt) if r_elt and not isinstance(r_elt, InterfaceType):
                                    if not getattr(l_type.Elt, "permanent_interface", False):
                                        l_type.Elt = r_elt
                                case ArrayType(Elt=e_elt), ArrayType(Elt=r_elt) if r_elt and not isinstance(r_elt, InterfaceType):
                                    if not compatible_types(r_elt, e_elt):
                                        l_type.Elt = InterfaceType()
                                        l_type.Elt.permanent_interface = True

            return node

        declared = self.apply_to_scope(node.Lhs, node.Rhs)
        if not declared:
            node.Tok = token.ASSIGN
        return node

    def apply_to_scope(self, lhs: list[Expr], rhs: list[Expr], rhs_is_types=False, force_current=False):
        # TODO: This was only built to handle one type, but zipping is much better sometimes
        ctx = {}
        for x in rhs:
            if isinstance(x, tuple):
                warnings.warn(f"Did not apply to scope context: {x}")  # TODO
            else:
                ctx.update(x._py_context)
        declared = False
        for i, expr in enumerate(lhs):
            match expr:
                case Ident():
                    t = rhs[i] if rhs_is_types else next((self.scope._get_type(x, force_current=force_current) for x in rhs), None)
                case _:
                    continue

            obj = Object(
                Data=None,
                Decl=None,
                Kind=ObjKind.Var,
                Name=expr.Name,
                Type=t,
                _py_context=ctx
            )
            if not (self.scope._in_scope(obj) or (
                    not force_current and (self.scope._in_outer_scope(obj) and (
                    # TODO: Combining nonlocals because I think it will technically
                    #   give better support than no support, but nonlocals needs further consideration
                    (obj.Name in self.current_globals + self.current_nonlocals) or not self.scope._global._in_scope(obj))
            )
            )):
                self.scope.Insert(obj)

                declared = True

            type_from_scope = self.scope._get_type(obj.Name, force_current=force_current)
            if type_from_scope:
                pass
            else:
                try:
                    t = rhs[i]
                except IndexError:
                    pass
                self.report_missing(expr, t)
        return declared

    def report_missing(self, expr, val, extra_callbacks=None):
        callbacks = [lambda *args, **kwargs: self.generic_missing_type_callback(*args, **kwargs)]
        if extra_callbacks:
            callbacks += extra_callbacks
        self.missing_type_info.append((expr, val, self.scope, callbacks))

    def generic_missing_type_callback(self, node: Expr, val: Expr, type_: Expr):
        return

    def apply_eager_context(self, lhs: list[Expr], rhs: list[Expr], rhs_is_types=False, force_current=False):
        if len(lhs) == len(rhs) and len(lhs) > 1:
            for x, y in zip(lhs, rhs):
                self.apply_eager_context([x], [y], rhs_is_types=rhs_is_types)
            return
        eager_type_hint = next((self.scope._get_type(x, force_current=force_current) for x in rhs), None)
        eager_context = {}
        for x in rhs:
            if isinstance(x, tuple):
                warnings.warn(f"Did not apply to eager context: {x}")  # TODO
            else:
                eager_context.update(x._py_context)
        for i, expr in enumerate(lhs):
            if not expr._type_help:
                expr._type_help = rhs[i] if rhs_is_types else eager_type_hint
            if eager_context:
                expr._py_context = {**eager_context, **expr._py_context}

    def add_callback_for_missing_type(self, node: Expr, callback: callable) -> bool:
        for expr, val, scope, callbacks in self.missing_type_info:
            if expr == node and self.scope._contains_scope(scope):
                callbacks.append(callback)
                return True
        return False


class IndexExpressionsHelpTypeMaps(NodeTransformerWithScope):
    def visit_IndexExpr(self, node: IndexExpr):
        self.generic_visit(node)
        x_type = self.scope._get_type(node.X)
        match x_type:
            case MapType(Key=InterfaceType()):
                x_type.Key._py_context.setdefault("elts", []).append(node.Index)
        return node

class AppendSliceViaUnpacking(NodeTransformerWithScope):
    def visit_AssignStmt(self, node: AssignStmt):
        node = super().visit_AssignStmt(node)
        match node:
            case AssignStmt(Rhs=[CompositeLit(), * ignored], Tok=token.ADD_ASSIGN):
                node.Rhs[0] = CallExpr(Args=[node.Lhs[0], node.Rhs[0]],
                                       Ellipsis=1, Fun=v("append"))
                node.Tok = token.ASSIGN
            case AssignStmt(Rhs=[BinaryExpr(Op=token.ADD, Y=CompositeLit()), * ignored]):
                node.Rhs[0] = CallExpr(Args=[node.Rhs[0].X, node.Rhs[0].Y],
                                       Ellipsis=1, Fun=v("append"))
            case AssignStmt(Lhs=[x], Rhs=[y], Tok=token.ADD_ASSIGN):
                x_type = self.scope._get_type(x)
                match x_type:
                    case ArrayType():
                        node.Rhs[0] = CallExpr(Args=[x, y],
                                               Ellipsis=1, Fun=v("append"))
                        node.Tok = token.ASSIGN
        return node


class ReplacePowWithMathPow(NodeTransformerWithScope):
    def visit_BinaryExpr(self, node: BinaryExpr):
        self.generic_visit(node)
        match node:
            case BinaryExpr(Op=token.PLACEHOLDER_POW):
                replacement = CallExpr(Args=[node.X, node.Y],
                                       Fun=SelectorExpr(X=v("math"), Sel=v("Pow")))
                x_type = self.scope._get_type(node.X)
                y_type = self.scope._get_type(node.Y)

                try:
                    x_basic = GoBasicType(x_type.Name)
                    y_basic = GoBasicType(y_type.Name)
                except (ValueError, AttributeError):
                    return replacement
                if x_basic.is_integer and y_basic.is_integer:
                    return replacement.cast(GoBasicType.FLOAT64.ident, get_dominant_type(x_type, y_type))
                return replacement
        return node


class RangeRangeToFor(BaseTransformer):
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


class UnpackRange(BaseTransformer):
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


class NegativeIndexesSubtractFromLen(BaseTransformer):
    """
    Will need some sort of type checking to ensure this doesn't affect maps or similar
    once map support is even a thing
    """

    def visit_IndexExpr(self, node: IndexExpr):
        self.generic_visit(node)
        match node.Index:
            case UnaryExpr(Op=token.SUB, X=BasicLit()):
                node.Index = BinaryExpr(X=CallExpr(Args=[node.X], Fun=v("len")),
                                        Op=token.SUB, Y=node.Index.X)
        return node


def wrap_with_call_to(args, wrap_with):
    if not isinstance(args, list):  # args must be an iterable but if it's not a list convert it to one
        args = list(args)
    if "." in wrap_with:
        x, sel = wrap_with.split(".")
        func = SelectorExpr(X=v(x), Sel=v(sel))
    else:
        func = v(wrap_with)
    return CallExpr(Args=args, Ellipsis=0, Fun=func, Lparen=0, Rparen=0)


class StringifyStringMember(NodeTransformerWithScope):
    """
    "Hello"[0] in Python is "H" but in Go it's a byte. Let's cast those back to string
    """

    def visit_IndexExpr(self, node: IndexExpr):
        self.generic_visit(node)
        if self.scope._get_type(node.X) == GoBasicType.STRING.ident and self.scope._get_type(
                node.Index) == GoBasicType.INT.ident:
            return GoBasicType.STRING.ident.call(node)
        return node


class FileWritesAndErrors(NodeTransformerWithScope):
    REPEATABLE = False
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node:
            case CallExpr(Fun=SelectorExpr(X=Ident(Name="os"), Sel=Ident(Name="OpenFile"))):
                f = v("f", _type_help=node._type(), _py_context=node._py_context)
                assignment = AssignStmt([f, v(UNHANDLED_ERROR)], [node], token.DEFINE)
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
                n = v("n")
                selector = "WriteString" if self.scope._get_ctx(node.Fun.X)['text_mode'] else "Write"
                return CallExpr(Args=[], Fun=FuncLit(
                    Body=BlockStmt(
                        List=[
                            AssignStmt([n, v(UNHANDLED_ERROR)], [
                                CallExpr(Args=node.Args, Fun=node.Fun.X.sel(selector))
                            ], token.DEFINE),
                            ReturnStmt([n])
                        ],
                    ),
                    Type=FuncType(Results=FieldList(List=[Field(Type=GoBasicType.INT.ident)]))
                ))
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="read"))):
                content = v("content")
                text_mode = self.scope._get_ctx(node.Fun.X)['text_mode']
                expr = CallExpr(Args=[], Fun=FuncLit(
                    Body=BlockStmt(
                        List=[
                            AssignStmt(Lhs=[content, v(UNHANDLED_ERROR)], Rhs=[
                                v("ioutil").sel("ReadAll").call(node.Fun.X)
                            ], Tok=token.DEFINE),
                            ReturnStmt(Results=[
                                CallExpr(Fun=GoBasicType.STRING.ident, Args=[content]) if text_mode else content])
                        ],
                    ),
                    Type=FuncType(Results=FieldList(List=[
                        Field(Type=GoBasicType.STRING.ident if text_mode else ArrayType.from_Ident(
                            GoBasicType.BYTE.ident))]))
                ))
                return expr
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="decode"))):
                string = GoBasicType.STRING.ident
                return string.call(node.Fun.X)
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name="encode"))):
                bytes_array = ArrayType(Elt=GoBasicType.BYTE.ident)
                return bytes_array.call(node.Fun.X)
        return node


def _type_score(typ):
    if isinstance(typ, InterfaceType):
        return -2
    if isinstance(typ, (MapType, ArrayType)):
        return -1
    try:
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
        ].index(str(typ.Name).lower())
    except ValueError:
        return float('inf')


def get_dominant_type(type_a: Expr, type_b: Expr, op: Optional[token] = None):
    # Pick a type to coerce things to
    if isinstance(type_a, GoBasicType):
        type_a = type_a.ident
    if isinstance(type_b, GoBasicType):
        type_b = type_b.ident

    return max((type_a, type_b), key=_type_score)


class HandleTypeCoercion(NodeTransformerWithScope):
    def visit_BinaryExpr(self, node: BinaryExpr):
        self.generic_visit(node)
        x_type, y_type = self.scope._get_type(node.X), self.scope._get_type(node.Y)
        match node.Op:
            case token.PLACEHOLDER_FLOOR_DIV:
                node.Op = token.QUO
                if x_type != GoBasicType.INT.ident or y_type != GoBasicType.INT.ident:
                    if x_type == GoBasicType.INT.ident:
                        node.X = GoBasicType.FLOAT64.ident.call(node.X)
                    if y_type == GoBasicType.INT.ident:
                        node.Y = GoBasicType.FLOAT64.ident.call(node.Y)
                    return wrap_with_call_to([node], "math.Floor")
            case token.QUO:
                if x_type == GoBasicType.INT.ident:
                    node.X = GoBasicType.FLOAT64.ident.call(node.X)
                    x_type = GoBasicType.FLOAT64.ident
                if y_type == GoBasicType.INT.ident:
                    node.Y = GoBasicType.FLOAT64.ident.call(node.Y)
                    y_type = GoBasicType.FLOAT64.ident
        if node.Op not in [token.PLACEHOLDER_IN, token.PLACEHOLDER_NOT_IN]:
            if x_type != y_type and x_type and y_type:
                true = Ident('true')
                false = Ident('false')

                # When comparing numbers to boolean literals, change the bools to ints
                if node.X == true and y_type.is_numeric_type:
                    node.X = BasicLit.from_int(1)
                    x_type = node.X._type()
                elif node.X == false and y_type.is_numeric_type:
                    node.X = BasicLit.from_int(0)
                    x_type = node.X._type()
                elif node.Y == true and x_type.is_numeric_type:
                    node.Y = BasicLit.from_int(1)
                    y_type = node.Y._type()
                elif node.Y == false and x_type.is_numeric_type:
                    node.Y = BasicLit.from_int(0)
                    y_type = node.Y._type()

                dominant_type = get_dominant_type(x_type, y_type, node.Op)

                if x_type != dominant_type:
                    node.X = node.X.cast(x_type, dominant_type)
                if y_type != dominant_type:
                    node.Y = node.Y.cast(y_type, dominant_type)

                # Simplify boolean comparisons
                for a, b in (node.X, node.Y), (node.Y, node.X):
                    if b == true:
                        return a
                    if b == false:
                        match a:
                            case BinaryExpr(Op=x):
                                if x in OP_COMPLIMENTS:
                                    a.Op = OP_COMPLIMENTS[x]
                                    return a
                        return a.not_()

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
            node.Lhs.append(v(UNHANDLED_HTTP_ERROR))
            self.scope.Objects[node.Lhs[0].Name].Type = HTTP_RESPONSE_TYPE
        return node

    def visit_SelectorExpr(self, node: SelectorExpr):
        if self.scope._get_type(node.X) == HTTP_RESPONSE_TYPE:
            match node.Sel.Name:
                case "text":
                    return CallExpr(Args=[], Fun=FuncLit(
                        Body=BlockStmt(
                            List=[
                                AssignStmt([v("body"), v(UNHANDLED_ERROR)], [
                                    _call_from_name("ioutil.ReadAll", [_selector_from_name(f"{node.X.Name}.Body")])
                                ], token.DEFINE),
                                ReturnStmt([wrap_with_call_to([v("body")], GoBasicType.STRING.value)])
                            ],
                        ),
                        Type=FuncType(Results=FieldList(List=[
                            Field(Type=v(GoBasicType.STRING.value))]))
                    ))
        return node


def _selector_from_name(name: str):
    parts = reversed(name.split("."))
    parts = [v(x) for x in parts]
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
                                               ExprStmt(X=wrap_with_call_to([v("err")], "panic"))], 0),
                                           Cond=BinaryExpr(X=v("err"), Op=token.NEQ,
                                                           Y=v("nil"), OpPos=0),
                                           Else=None,
                                           If=0,
                                           Init=None,
                                       ))
            for j, deferred_call in enumerate(unhandled_defers):
                pos += 1
                block_node.List.insert(pos, DeferStmt(deferred_call, 0))

        return block_node


class AddTextTemplateImportForFStrings(BaseTransformer):
    """
    Usually goimports makes these sorts of things unnecessary,
    but this one was getting confused with html/template sometimes
    """

    def __init__(self):
        super().__init__()
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


def _map_contains(node: BinaryExpr):
    # Check if a bin expression's MapType Y contains X
    ok = v("ok")
    return FuncLit(
        Body=BlockStmt(List=[
            AssignStmt(Lhs=[v("_"), ok], Rhs=[node.Y[node.X]], Tok=token.DEFINE),
            ReturnStmt(Results=[ok])
        ]),
        Type=FuncType(Results=FieldList(List=[Field(Type=v("bool"))]))
    ).call()


# TODO: Should check scope
class UseConstructorIfAvailable(BaseTransformer):
    def __init__(self):
        super().__init__()
        self.declared_function_names = {}

    def visit_FuncDecl(self, node: FuncDecl):
        self.generic_visit(node)
        self.declared_function_names[node.Name.Name] = node.Name
        return node

    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node.Fun:
            case Ident(Name=x):
                if f"New{x}" in self.declared_function_names:
                    node.Fun = self.declared_function_names[f"New{x}"]
        return node


class SpecialComparators(NodeTransformerWithScope):
    def visit_BinaryExpr(self, node: BinaryExpr):
        self.generic_visit(node)
        match node.Op:
            case token.PLACEHOLDER_IN:
                node.Op = token.NEQ
                match self.scope._get_type(node.Y):
                    case GoBasicType.STRING.ident:
                        node = v("strings").sel("Contains").call(node.Y, node.X)
                    case ArrayType(Elt=Ident(Name=x)) if x in [GoBasicType.BYTE.value, GoBasicType.UINT8.value]:
                        node = v("bytes").sel("Contains").call(node.Y, node.X)
                    case MapType():
                        node = _map_contains(node)
                    case _:
                        node.X = ast_snippets.index(node.Y, node.X)
                        node.Y = BasicLit.from_int(-1)
            case token.PLACEHOLDER_NOT_IN:
                node.Op = token.EQL
                match self.scope._get_type(node.Y):
                    case GoBasicType.STRING.ident:
                        node = v("strings").sel("Contains").call(node.Y, node.X)
                        node = UnaryExpr(Op=token.NOT, X=node)
                    case ArrayType(Elt=Ident(Name=x)) if x in [GoBasicType.BYTE.value, GoBasicType.UINT8.value]:
                        node = v("bytes").sel("Contains").call(node.Y, node.X)
                        node = UnaryExpr(Op=token.NOT, X=node)
                    case MapType():
                        node = UnaryExpr(Op=token.NOT, X=_map_contains(node))
                    case _:
                        node.X = ast_snippets.index(node.Y, node.X)
                        node.Y = BasicLit.from_int(-1)
            case token.PLACEHOLDER_IS:
                node.Op = token.EQL
                node.X = node.X.ref()
                node.Y = node.Y.ref()
            case token.PLACEHOLDER_IS_NOT:
                node.Op = token.NEQ
                node.X = node.X.ref()
                node.Y = node.Y.ref()
            case token.EQL | token.NEQ:
                for xy in (node.X, node.Y):
                    t = self.scope._get_type(xy)
                    match t:
                        case MapType() | ArrayType() | FuncType() | InterfaceType():
                            reflect = Ident("reflect")
                            result = reflect.sel("DeepEqual").call(node.X, node.Y)
                            if node.Op == token.NEQ:
                                result = result.not_()
                            return result

        return node


class AsyncTransformer(BaseTransformer):
    def visit_UnaryExpr(self, node: UnaryExpr):
        self.generic_visit(node)
        # Change awaited asyncio calls
        match node:
            case UnaryExpr(X=CallExpr(Fun=SelectorExpr(X=Ident(Name="asyncio"), Sel=sel), Args=args)):
                match sel:
                    case Ident(Name="sleep"):
                        time = Ident("time")
                        # TODO: Ignored optional result keyword
                        return time.sel("Sleep").call(time.sel("Second") * args[0])
        return node


# class AddMissingFunctionTypes(NodeTransformerWithScope):
#     def visit_BlockStmt(self, node: BlockStmt):
#         self.generic_visit(node)
#         if hasattr(node, 'parent'):
#             print()
#         return node
#
# def visit_FuncDecl(self, node: FuncDecl):
#     node.Body.parent = node
#     self.generic_visit(node)
#     if node.Type.Results is None:
#         return_stmts = _find_nodes(
#             node.Body,
#             finder=lambda x: x if isinstance(x, ReturnStmt) else None,
#             skipper=lambda x: isinstance(x, FuncLit)
#         )
#
#         if return_stmts:
#             for return_stmt in return_stmts:
#                 return_stmt: ReturnStmt
#                 types = [x._type() for x in return_stmt.Results]
#                 if all(types):
#                     results = FieldList(List=[Field(Type=t) for t in types])
#                     node.Type.Results = results
#     return node


class YieldTransformer(NodeTransformerWithScope):
    REPEATABLE = False
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        match node:
            case CallExpr(Fun=Ident(Name="next"), Args=[chan]):
                return chan.call().receive()
        return node

    def visit_FuncDecl_or_FuncLit(self, node: FuncDecl | FuncLit):
        super().visit_FuncDecl_or_FuncLit(node)

        def finder(x: GoAST):
            match x:
                case SendStmt(Chan=Ident(Name=name)):
                    return x if name == 'yield' else None
            return None

        stmts = _find_nodes(
            node.Body,
            finder=finder,
            skipper=lambda x: isinstance(x, FuncLit)
        )


        if any(stmts):
            # TODO: Multi-support
            original_type = None
            for f in (node.Type.Results.List if node.Type.Results else []):
                original_type = f.Type
                f.Type = ChanType(Value=f.Type, Dir=2)
            if original_type is None:
                return node
            return_func_type = node.Type
            node.Type = FuncType(Params=FieldList(), Results=FieldList(List=[Field(Type=node.Type)]))
            wait = Ident("wait")
            _yield = Ident("yield")
            make = Ident("make")
            node.Body.List[:] = [
                wait.assign(make.call(StructType().chan())),
                _yield.assign(make.call(original_type.chan())),
                FuncLit(Body=BlockStmt(List=[
                    Ident("close").call(_yield).defer(),
                    wait.receive().stmt(),
                    *node.Body.List,
                ])).call().go(),
                FuncLit(Type=return_func_type, Body=BlockStmt(List=[
                    wait.send(StructType().composite_lit_type()),
                    _yield.return_()
                ])).return_()
            ]

        return node


class YieldRangeTransformer(NodeTransformerWithScope):
    REPEATABLE = False
    def visit_RangeStmt(self, node: RangeStmt, callback=False, callback_type=None, callback_parent=None):
        if not callback:
            self.generic_visit(node)
        node.X = self.generic_visit(node.X)
        t = callback_type or self.scope._get_type(node.X)
        match t:
            case None:
                _callback_parent = self.stack[-1] if len(self.stack) > 1 else None
                self.add_callback_for_missing_type(node.X, (lambda _, __, type_: self.visit_RangeStmt(
                    node, callback=True, callback_type=type_, callback_parent=_callback_parent)))
            case FuncType(Results=FieldList(List=[Field(Type=FuncType(Results=FieldList(List=[Field(Type=ChanType())])))])) | FuncType(Results=FieldList(List=[Field(Type=ChanType())])):
                val = node.Value
                gen = node.X
                ok = Ident("ok")
                for_stmt = ForStmt(
                    Body=node.Body,
                    Init=AssignStmt(Lhs=[val, ok], Rhs=[gen.call().receive()], Tok=token.DEFINE),
                    Cond=ok,
                    Post=AssignStmt(Lhs=[val, ok], Rhs=[gen.call().receive()], Tok=token.ASSIGN)
                )
                if callback and callback_parent:
                    match callback_parent:
                        case BlockStmt(List=l):
                            l: list
                            old_index = l.index(node)
                            l[old_index] = for_stmt
                        case _:
                            raise NotImplementedError()
                return for_stmt
        return node


class InitStmt(NodeTransformerWithScope):
    def visit_BadExpr(self, node: BadExpr):
        self.generic_visit(node)
        if not "NamedExpr" in node._py_context:
            return node

        assignment: AssignStmt = node._py_context["NamedExpr"]
        for to_initialize in reversed(self.stack):
            if hasattr(to_initialize, "Init"):
                break
        else:
            prev = node
            for i, to_insert_into in enumerate(reversed(self.stack)):
                if isinstance(to_insert_into, BlockStmt):
                    break
                prev = to_insert_into
            else:
                return assignment.Lhs[0]

            # Do this at the end because it messes with the transformer if we do it now
            def exit_callback(*args, **kwargs):
                insert_at = to_insert_into.List.index(prev)
                to_insert_into.List.insert(insert_at, assignment)

            self.exit_callbacks.append(exit_callback)

            return assignment.Lhs[0]

        if to_initialize.Init and isinstance(to_initialize.Init, AssignStmt):
            to_initialize.Init.Lhs += assignment.Lhs
            to_initialize.Init.Rhs += assignment.Rhs
        else:
            to_initialize.Init = assignment

        if isinstance(to_initialize, ForStmt):
            if to_initialize.Post and isinstance(to_initialize.Post, AssignStmt):
                to_initialize.Post.Lhs += assignment.Lhs
                to_initialize.Post.Rhs += assignment.Rhs
            else:
                to_initialize.Post = AssignStmt(Lhs=assignment.Lhs.copy(), Rhs=assignment.Rhs.copy(), Tok=token.ASSIGN)

        return assignment.Lhs[0]


class FillDefaultsAndSortKeywords(NodeTransformerWithScope):
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        return node

    def generic_missing_type_callback(self, node: Expr, val: Expr, type_: Expr):
        if not isinstance(type_, FuncType):
            return

        if not type_.Params or "defaults" not in type_.Params._py_context:
            return

        match val:
            case CallExpr():
                val: CallExpr

                # Remove and set aside keyword arguments
                call_kw_args = {}
                call_kw_arg_indices = []
                for i, arg in enumerate(val.Args):
                    if "keyword" in arg._py_context:
                        call_kw_args[arg._py_context["keyword"]] = arg
                        call_kw_arg_indices.append(i)
                for i in reversed(call_kw_arg_indices):
                    del val.Args[i]

                # Add missing args
                adding = []
                for default in reversed(type_.Params._py_context["defaults"]):
                    if len(val.Args) + len(adding) >= len(type_.Params.List):
                        break
                    adding.append(default)
                val.Args += reversed(adding)

                # Fill in any keyword args in proper positions
                arg_names = []
                for param in type_.Params.List:
                    for name in param.Names:
                        arg_names.append(name.Name)

                for kwname, kwvalue in call_kw_args.items():
                    try:
                        val.Args[arg_names.index(kwname)] = kwvalue
                    except IndexError:
                        warnings.warn("TODO: *args, **kwargs? Oh boy...")
                        continue

        return


class Truthiness(NodeTransformerWithScope):
    def visit_IfStmt(self, node: IfStmt):
        self.generic_visit(node)
        if node.Cond and (type_ := self.scope._get_type(node.Cond)):
            node.Cond = node.Cond.cast(type_, Ident("bool"))
        return node

    def visit_ForStmt(self, node: ForStmt):
        self.generic_visit(node)
        if node.Cond and (type_ := self.scope._get_type(node.Cond)):
            node.Cond = node.Cond.cast(type_, Ident("bool"))
        return node

    def generic_missing_type_callback(self, node: Expr, val: Expr, type_: Expr):
        if hasattr(node, "Cond"):
            node.Cond = node.Cond.cast(type_, Ident("bool"))


class IterFuncs(NodeTransformerWithScope):
    # TODO: Deprecate via pysnippets
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        if len(node.Args) == 0:
            return node
        if len(node.Args) == 1:
            t = self.scope._get_type(node.Args[0])
            iterable = node.Args[0]
        else:
            # TODO: This will create ugly functions so fix it
            t = ArrayType(Elt=self.scope._get_type(node.Args[0]))
            iterable = CompositeLit(Elts=node.Args, Type=t)

        if not isinstance(t, ArrayType):  # TODO: Support other types that can be min'd/max'd/etc
            return node

        et = t.Elt
        match node:
            case CallExpr(Fun=Ident(Name=x)):
                match x:
                    case 'max' | 'min' | 'sum':
                        iterable: Expr
                        m = Ident('m')
                        i = Ident('i')
                        e = Ident('e')
                        if x in ['min', 'max']:
                            key = (e < m) if x == 'min' else (e > m)
                            loop_body = [
                                i.eql(BasicLit.from_int(0)).or_(key).if_(
                                    [m.assign(e, tok=token.ASSIGN)]
                                )
                            ]
                        elif x == 'sum':
                            i = Ident("_")
                            m = Ident("s")
                            loop_body = [
                                m.assign(e, tok=token.ADD_ASSIGN)
                            ]
                        return FuncLit(
                            Type=FuncType(
                                Results=FieldList(List=[
                                    Field(Names=[m], Type=et)
                                ])
                            ),
                            Body=BlockStmt(List=[
                                RangeStmt(
                                    Key=i,
                                    Value=e,
                                    X=iterable,
                                    Tok=token.DEFINE,
                                    Body=BlockStmt(List=loop_body)
                                ),
                                ReturnStmt()
                            ])
                        ).call()
                    case "reversed":
                        i = Ident("i")
                        e = Ident("e")
                        arr = Ident("arr")
                        arr2 = Ident("arr2")

                        setup_body = [
                            arr2.assign(Ident("make").call(t, len_(arr))),
                        ]
                        loop_body = [
                            arr2[len_(arr) - i - 1].assign(e, tok=token.ASSIGN)
                        ]

                        return FuncLit(
                            Type=FuncType(
                                Params=FieldList(List=[
                                    Field(Names=[arr], Type=t)
                                ]),
                                Results=FieldList(List=[
                                    Field(Type=t)
                                ])
                            ),
                            Body=BlockStmt(List=[
                                *setup_body,
                                RangeStmt(
                                    Key=i, Value=e, X=arr,
                                    Body=BlockStmt(List=loop_body),
                                    Tok=token.DEFINE,
                                ),
                                ReturnStmt(Results=[arr2])
                            ])
                        ).call(iterable)

        return node


class IterMethods(NodeTransformerWithScope):
    # TODO: Deprecate via pysnippets
    def visit_CallExpr(self, node: CallExpr):
        self.generic_visit(node)
        if len(node.Args) != 0:
            return node
        if not isinstance(node.Fun, SelectorExpr):
            return node

        iterable = node.Fun.X
        t = self.scope._get_type(iterable)

        if not isinstance(t, ArrayType):  # TODO: Support other types that can be min'd/max'd/etc
            return node

        et = t.Elt
        match node:
            case CallExpr(Fun=SelectorExpr(Sel=Ident(Name=x))):
                match x:
                    case "reverse":
                        i = Ident("i")
                        j = Ident("j")
                        arr = Ident("arr")
                        init = AssignStmt(Lhs=[i, j], Rhs=[BasicLit.from_int(0), len_(arr) - 1], Tok=token.DEFINE)
                        cond = i < j
                        post = AssignStmt(Lhs=[i, j], Rhs=[i + 1, j - 1], Tok=token.ASSIGN)
                        loop_body = [
                            AssignStmt(Lhs=[arr[i], arr[j]], Rhs=[arr[j], arr[i]])
                        ]

                        return FuncLit(
                            Type=FuncType(
                                Params=FieldList(List=[
                                    Field(Names=[arr], Type=t)
                                ])
                            ),
                            Body=BlockStmt(List=[
                                ForStmt(
                                    Init=init,
                                    Cond=cond,
                                    Post=post,
                                    Body=BlockStmt(List=loop_body)
                                ),
                            ])
                        ).call(iterable)
        return node


class InitializeNamedParamMaps(NodeTransformerWithScope):
    REPEATABLE = False
    def visit_FuncDecl_or_FuncLit(self, node: FuncDecl | FuncLit):
        super().visit_FuncDecl_or_FuncLit(node)
        if not node.Type.Results:
            return node
        for field in node.Type.Results.List:
            if isinstance(field.Type, MapType):
                for name in reversed(field.Names):
                    node.Body.List.insert(0, name.assign(Ident("make").call(field.Type), tok=token.ASSIGN))
        return node

class RemoveGoCallReturns(BaseTransformer):
    """
    Hack to remove erroneously annotated function calls
    """
    def visit_GoStmt(self, node: GoStmt):
        self.generic_visit(node)
        node.Call.Fun.Type.Results = None
        return node

class RemoveBadStmt(BaseTransformer):
    def visit_BadStmt(self, node: BadStmt):
        self.generic_visit(node)
        pass  # It is removed by not being returned


class PySnippetSwitches(NodeTransformerWithScope):
    def visit_CallExpr(self, node: CallExpr):
        node = self.generic_visit(node)
        if 'py_snippet' not in node._py_context:
            return node

        snippet = node._py_context["py_snippet"]

        if not isinstance(node.Fun, FuncLit):
            return node
        match node.Fun.Body.List:
            case [TypeSwitchStmt() as x]:
                x_param = x.Assign.X.X
                x_param_index = -1
                for i, field in enumerate(node.Fun.Type.Params.List):
                    if x_param in field.Names:
                        x_param_index = i

                x_arg = node.Args[x_param_index]
                x_type = self.scope._get_type(x_arg)
                for case in x.Body.List:
                    match case.List:
                        case [y_type]:
                            if y_type == x_type:
                                break

                param_mapping = {}
                for param, arg in zip(node.Fun.Type.Params.List, node.Args):
                    for name in param.Names:
                        param_mapping[name.Name] = arg

                keep_params = False
                match snippet.name:
                    case r'(.*)\.index':
                        match x_type:
                            case Ident(Name="string"):
                                keep_params = True

                stmts = case.Body
                if not keep_params:
                    class Transformer(BaseTransformer):
                        def visit_Ident(self, node: Ident):
                            self.generic_visit(node)
                            return param_mapping.get(node.Name, node)

                    for stmt in stmts:
                        Transformer().visit(stmt)

                if len(stmts) == 1:
                    if isinstance(stmts[0], ExprStmt):
                        return stmts[0].X
                    return stmts[0]

                if not keep_params:
                    node.Args[:] = []
                    node.Fun.Type.Params.List[:] = []
                node.Fun.Body.List[:] = stmts
        return node

class NodeTransformerWithInterfaceTypes(NodeTransformerWithScope):
    # TODO: Optimize. This is way too f**ing slow
    def visit_InterfaceType(self, node: InterfaceType):
        self.generic_visit(node)
        if getattr(node, "permanent_interface", False):
            return node
        elts = node._py_context.get("elts", [])
        if not elts:
            return node

        for parent in reversed(self.stack):
            elt_types = []

            class MetaVisitor(NodeTransformerWithScope):
                def __init__(self):
                    super().__init__()

                def visit_InterfaceType(s, node: InterfaceType):
                    s.generic_visit(node)
                    return node

                def generic_visit(s, node):
                    node = super().generic_visit(node)

                    if not elt_types:
                        for elt in elts:
                            t = s.scope._get_type(elt)

                            if not t:
                                match node:
                                    case RangeStmt(Value=v, X=x) if v == elt:
                                        x_type = s.scope._get_type(x)
                                        match x_type:
                                            case ArrayType(Elt=y) | MapType(Value=y):
                                                t = y
                                    case FuncDecl() if isinstance(elt, CallExpr) and isinstance(elt.Fun, Ident):
                                        if elt.Fun == node.Name:
                                            if node.Type.Results and node.Type.Results.List:
                                                t = node.Type.Results.List[0].Type  # TODO: Another multi result issue
                            if t:
                                elt_types.append(t)

                    return node

            MetaVisitor().visit(parent)
            if elt_types:
                for elt_type_1, elt_type_2 in zip(elt_types[:-1], elt_types[1:]):
                    if elt_type_1 != elt_type_2:
                        break
                else:
                    return elt_types[-1]

        return node

class UntypedFunctionsTypedByCalls(NodeTransformerWithScope):
    def visit_CallExpr(self, node: CallExpr):
        node = self.generic_visit(node)
        scope = self.scope
        def exit_callback(*args, **kwargs):
            fun_type = node.Fun.basic_type or scope._get_type(node.Fun)
            match fun_type:
                case FuncType(Params=FieldList(List=params)) | FuncDecl(Type=FuncType(Params=FieldList(List=params))):
                    for i, param in enumerate(params):
                        match param.Type:
                            case InterfaceType() | None:
                                if getattr(param.Type, "permanent_interface", False):
                                    continue
                                try:
                                    arg = node.Args[i]
                                except IndexError:  # TODO: Happened with Files. Probably because of adding an extra "err" with f = -> f, err =
                                    break
                                arg_type = scope._get_type(arg)
                                if arg_type and not isinstance(arg_type, InterfaceType):
                                    param.Type = arg_type
                                    continue
        self.exit_callbacks.append(exit_callback)
        return node

class CallTypeInformation(NodeTransformerWithScope):
    def visit_CallExpr(self, node: CallExpr):
        # Specifically fixes function signatures, meant to fix bug with go_copy
        discoveries = 0
        match node.Fun:
            case Ident(Name="copy") | Ident(Name="append"):
                a, b = node.Args
                a_type = self.scope._get_type(a)
                b_type = self.scope._get_type(b)
                for x, x_type, y_type in ((b, b_type, a_type), (a, a_type, b_type)):
                    match x_type:
                        case None | InterfaceType() | StarExpr(X=InterfaceType()):
                            match x_type:
                                case InterfaceType():
                                    if getattr(x_type, "permanent_interface", False):
                                        return node
                                case StarExpr():
                                    if getattr(x_type.X, "permanent_interface", False):
                                        return node
                            if y_type:
                                self.apply_to_scope([x], [y_type], rhs_is_types=True, force_current=True)
                                discoveries += 1
                                break
            case FuncLit(Type=FuncType(Params=FieldList(List=func_args))) if func_args:
                for a, b in zip(node.Args, func_args):
                    a_type = self.scope._get_type(a)
                    b_type = b.Type
                    a_int = InterfaceTypeCounter.get_interface_count(a_type) if a_type else float('inf')
                    b_int = InterfaceTypeCounter.get_interface_count(b_type) if b_type else float('inf')
                    if b_int > a_int:
                        b.Type = a_type
                    elif a_int > b_int:
                        self.apply_to_scope([a], [b_type], rhs_is_types=True, force_current=True)
                        discoveries += 1


        if discoveries:
            stack = self.stack.copy()
            while stack and discoveries:
                parent = stack.pop()
                match parent:
                    case FuncLit(Type=FuncType() as t):
                        for x in [t.Params, t.Results]:
                            if isinstance(x, FieldList):
                                for field in x.List:
                                    match field.Type:
                                        case InterfaceType():
                                            if getattr(x_type, "permanent_interface", False):
                                                pass
                                            else:
                                                for name in field.Names:
                                                    t = self.scope._get_type(name)
                                                    if t:
                                                        field.Type = t
                                                        discoveries -= 1
                                                        break
                                        case StarExpr():
                                            for name in field.Names:
                                                t = self.scope._get_type(name)
                                                if t:
                                                    field.Type = t
                                                    discoveries -= 1
                                                    break
        self.generic_visit(node)
        return node

    def visit_InterfaceType(self, node: InterfaceType):
        node = self.generic_visit(node)
        if getattr(node, "permanent_interface", False):
            return node
        parent = self.stack[-1]
        interface_scope = self.scope
        def exit_callback(*args, **kwargs):
            if isinstance(parent, Field):
                for name in parent.Names:
                    t = interface_scope._get_type(name)
                    if t and not isinstance(t, InterfaceType):
                        parent.Type = t
                        break
        self.exit_callbacks.append(exit_callback)
        return node

    def generic_missing_type_callback(self, node: Expr, val: Expr, type_: Expr):
        return

class MergeAdjacentInits(BaseTransformer):
    def visit_File(self, node: File):
        decls = node.Decls
        i = 0
        while i < (len(decls) - 1):
            cur = decls[i]
            nxt = decls[i+1]
            match cur, nxt:
                case FuncDecl(Name=Ident(Name="init")), FuncDecl(Name=Ident(Name="init")):
                    cur.Body.List += nxt.Body.List
                    del decls[i+1]
                # Also try to group variable declarations/imports above init methods
                case FuncDecl(Name=Ident(Name="init")), GenDecl():
                    decls[i], decls[i+1] = decls[i+1], decls[i]
                    i += 1
                case _:
                    i += 1
        return node

class LoopThroughSetValuesNotKeys(NodeTransformerWithScope):
    def visit_RangeStmt(self, node: RangeStmt):
        self.generic_visit(node)
        x_type = self.scope._get_type(node.X)
        match x_type:
            case MapType(Value=StructType(Fields=FieldList(List=[]))):
                if node.Key == Ident("_"):
                    node.Key, node.Value = node.Value, node.Key
        return node


class LoopThroughFileLines(NodeTransformerWithScope):
    def visit_RangeStmt(self, node: RangeStmt):
        self.generic_visit(node)
        x_type = self.scope._get_type(node.X)
        match x_type:
            case StarExpr(X=SelectorExpr(X=Ident(Name="os"), Sel=Ident(Name="File"))):
                return ast_snippets.file_loop(node.Value, node.X, node.Body)
        return node


class RemoveUnnecessaryFunctionLiterals(NodeTransformerWithScope):
    def visit_FuncDecl(self, node: FuncDecl):
        return self.visit_FuncDecl_or_FuncLit(node)

    def visit_FuncLit(self, node: FuncLit):
        return self.visit_FuncDecl_or_FuncLit(node)

    def visit_FuncDecl_or_FuncLit(self, node: FuncDecl | FuncLit):
        """
        func (*) (*) { func() { do_something }() } -> func (*) (*) { do_something }
        """
        self.generic_visit(node)
        match node.Body.List:
            case [ExprStmt(X=CallExpr(Args=[], Fun=FuncLit(Type=FuncType(Results=results, Params=params)) as x))]:
                if results is None or results == FieldList(List=[]) and params is None or params == FieldList(List=[]):
                    node.Body.List.pop()
                    node.Body.List += x.Body.List
        return node



class TypeSwitchStatementsRedeclareWithType(NodeTransformerWithScope):
    def visit_TypeSwitchStmt(self, node: TypeSwitchStmt):
        self.generic_visit(node)
        match node.Assign:
            case ExprStmt(X=TypeAssertExpr(X=Ident() as expr)):
                if expr in node.Body:
                    node.Assign = AssignStmt(Lhs=[expr], Tok=token.DEFINE, Rhs=[node.Assign.X])
        return node


ALL_TRANSFORMS = [
    #### STAGE 0 ####
    InsertUniqueInitializers,
    ApplyPytagoInlines,

    #### STAGE 1 ####
    UseConstructorIfAvailable,
    PrintToFmtPrintln,
    CapitalizeMathModuleCalls,
    ReplacePythonStyleAppends,
    PythonToGoTypes,
    UnpackRange,
    RangeRangeToFor,
    SpecialComparators,  # First scope transformer
    IndexExpressionsHelpTypeMaps,
    AppendSliceViaUnpacking,
    YieldTransformer,  # May need to be above other scope transformers because jank,
    YieldRangeTransformer,
    ReplacePowWithMathPow,
    NodeTransformerWithScope,
    LoopThroughSetValuesNotKeys,
    LoopThroughFileLines,
    # AddMissingFunctionTypes,
    IterFuncs,
    IterMethods,
    NegativeIndexesSubtractFromLen,
    StringifyStringMember,
    HandleTypeCoercion,
    RequestsToHTTP,
    HTTPErrors,
    FileWritesAndErrors,
    HandleUnhandledErrorsAndDefers,
    AddTextTemplateImportForFStrings,
    AsyncTransformer,
    InitStmt,
    FillDefaultsAndSortKeywords,
    Truthiness,
    InitializeNamedParamMaps,
    PySnippetSwitches,
    CallTypeInformation,
    UntypedFunctionsTypedByCalls,
    NodeTransformerWithInterfaceTypes,
    TypeSwitchStatementsRedeclareWithType,
    RemoveUnnecessaryFunctionLiterals,
    RemoveGoCallReturns,  # Needs to be below scoping functions or they'll just get added back
    RemoveBadStmt,  # Should be last as these are used for scoping
    MergeAdjacentInits,

    #### STAGE 2 ####
    RemoveIfNameEqualsMain
]