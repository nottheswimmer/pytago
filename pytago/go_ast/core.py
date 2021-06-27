import ast
import inspect
import json
import traceback
import warnings
from enum import Enum
from functools import cached_property
from typing import List, Dict, Optional, Any, TypeVar, Type, Callable

from pytago.go_ast import ast_snippets
from pytago.go_ast.py_snippets import find_call_funclit


class ObjKind(Enum):
    Bad = "bad"
    Pkg = "package"
    Con = "const"
    Typ = "type"
    Var = "var"
    Fun = "func"
    Lbl = "label"


class GoBasicType(Enum):
    BOOL = "bool"
    UINT8 = "uint8"
    BYTE = "byte"  # Alias for UINT8
    UINT16 = "uint16"
    UINT32 = "uint32"
    UINT64 = "uint64"
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    RUNE = "rune"  # Alias for INT32
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"
    COMPLEX64 = "complex64"
    COMPLEX128 = "complex128"
    STRING = "string"
    INT = "int"
    UINT = "uint"
    UINTPTR = "uintptr"

    @cached_property
    def ident(self):
        return Ident.from_str(self.value)

    @cached_property
    def is_signed_integer(self):
        t = self.__class__
        return self in [t.INT8, t.INT16, t.INT32, t.RUNE, t.INT64, t.INT]

    @cached_property
    def is_unsigned_integer(self):
        t = self.__class__
        return self in [t.UINT8, t.BYTE, t.UINT16, t.UINT32, t.UINT64, t.UINT, t.UINTPTR]

    @cached_property
    def is_integer(self):
        return self.is_signed_integer or self.is_unsigned_integer

    @cached_property
    def is_float(self):
        t = self.__class__
        return self in [t.FLOAT32, t.FLOAT64]

    @cached_property
    def is_complex(self):
        t = self.__class__
        return self in [t.COMPLEX64, t.COMPLEX128]

    @cached_property
    def is_numeric(self):
        return self.is_integer or self.is_float or self.is_complex


# class GoCompositeType(Enum):
#     ARRAY = "array"
#     STRUCT = "struct"
#     POINTER = "pointer"
#     FUNCTION = "function"
#     INTERFACE = "interface"
#     SLICE = "slice"
#     MAP = "map"
#     CHANNEL = "channel"


class token(Enum):
    ILLEGAL = "ILLEGAL"

    EOF = "EOF"
    COMMENT = "COMMENT"

    IDENT = "IDENT"
    INT = "INT"
    FLOAT = "FLOAT"
    IMAG = "IMAG"
    CHAR = "CHAR"
    STRING = "STRING"

    ADD = "+"
    SUB = "-"
    MUL = "*"
    QUO = "/"
    REM = "%"

    AND = "&"
    OR = "|"
    XOR = "^"
    SHL = "<<"
    SHR = ">>"
    AND_NOT = "&^"

    ADD_ASSIGN = "+="
    SUB_ASSIGN = "-="
    MUL_ASSIGN = "*="
    QUO_ASSIGN = "/="
    REM_ASSIGN = "%="

    AND_ASSIGN = "&="
    OR_ASSIGN = "|="
    XOR_ASSIGN = "^="
    SHL_ASSIGN = "<<="
    SHR_ASSIGN = ">>="
    AND_NOT_ASSIGN = "&^="

    LAND = "&&"
    LOR = "||"
    ARROW = "<-"
    INC = "++"
    DEC = "--"

    EQL = "=="
    LSS = "<"
    GTR = ">"
    ASSIGN = "="
    NOT = "!"

    NEQ = "!="
    LEQ = "<="
    GEQ = ">="
    DEFINE = ":="
    ELLIPSIS = "..."

    LPAREN = "("
    LBRACK = "["
    LBRACE = "{"
    COMMA = ""
    PERIOD = "."

    RPAREN = ")"
    RBRACK = "]"
    RBRACE = "}"
    SEMICOLON = ";"
    COLON = ":"

    BREAK = "break"
    CASE = "case"
    CHAN = "chan"
    CONST = "const"
    CONTINUE = "continue"

    DEFAULT = "default"
    DEFER = "defer"
    ELSE = "else"
    FALLTHROUGH = "fallthrough"
    FOR = "for"

    FUNC = "func"
    GO = "go"
    GOTO = "goto"
    IF = "if"
    IMPORT = "import"

    INTERFACE = "interface"
    MAP = "map"
    PACKAGE = "package"
    RANGE = "range"
    RETURN = "return"

    SELECT = "select"
    STRUCT = "struct"
    SWITCH = "switch"
    TYPE = "type"
    VAR = "var"

    # Placeholders
    PLACEHOLDER_POW = "**"
    PLACEHOLDER_FLOOR_DIV = "//"
    PLACEHOLDER_IS = "is"
    PLACEHOLDER_IS_NOT = "is not"
    PLACEHOLDER_IN = "in"
    PLACEHOLDER_NOT_IN = "not in"


COMPARISON_OPS = [token.GTR,
                  token.GEQ,
                  token.LSS,
                  token.LEQ,
                  token.EQL,
                  token.NEQ]
BOOL_OPS = [
    token.LAND,
    token.LOR,
    token.NOT
]

OP_COMPLIMENTS = {
    token.GEQ: token.LEQ,
    token.GTR: token.LSS,
    token.EQL: token.NEQ,
}
OP_COMPLIMENTS |= {v: k for k, v in OP_COMPLIMENTS.items()}

class PY_DEREF_EXPR(): pass
def _type_annotation_to_go_type(node: ast.AST):
    match node:
        case ast.Name(id=x):
            match x:
                case 'str':
                    return GoBasicType.STRING.ident
                case 'int':
                    return GoBasicType.INT.ident
                case 'float':
                    return GoBasicType.FLOAT64.ident
                case 'complex':
                    return GoBasicType.COMPLEX128.ident
                case 'bytes' | 'bytearray':
                    return ArrayType(Elt=GoBasicType.BYTE.ident)
                case 'list' | 'tuple' | 'List' | 'Tuple':
                    return ArrayType()
                case 'dict' | 'Dict' | 'DefaultDict' | 'OrderedDict' | 'TypedDict' | 'Mapping' | 'MutableMapping':
                    return MapType()
                case 'set' | 'frozenset' | 'Set' | 'FrozenSet' | 'MutableSet':
                    return MapType(Value=StructType())
                case 'bool':
                    return Ident('bool')
                case 'PytagoInterfaceType':
                    return InterfaceType()
                case 'PytagoStarExpr':
                    return StarExpr()
                case _:
                    return Ident(x)
        case ast.Subscript(value=value, slice=index):
            value = _type_annotation_to_go_type(value)
            index = _type_annotation_to_go_type(index)
            match value:
                case ArrayType():
                    value.Elt = index
                case MapType():
                    if isinstance(index, tuple):
                        key, map = index
                        value.Key = key
                        value.Map = map
                    else:
                        # A set?
                        key = index
                        value.Key = key
                case InterfaceType():
                    return InterfaceType(_py_context={"elts": [index]})
                case StarExpr():
                    return StarExpr(X=index)
                case _:
                    raise NotImplementedError(value)
            return value
        case ast.Tuple(elts=elts):
            return tuple(_type_annotation_to_go_type(elt) for elt in elts)
        case ast.Attribute():
            return build_expr_list([node])[0]
        case _:
            raise NotImplementedError(node)

def _only_truthy(elts):
    return [elt for elt in elts if elt]

def _find_nodes(node: ast.AST, finder: callable, skipper: callable=None):
    results = []
    class Explorer(ast.NodeVisitor):
        def generic_visit(self, node: ast.AST) -> Any:
            if skipper and skipper(node):
                return node
            if result := finder(node):
                results.append(result)
            return super().generic_visit(node)
    Explorer().visit(node)
    return results

def _replace_nodes(node: ast.AST, replacer: callable, skipper: callable=None):
    results = []
    class Replacer(ast.NodeTransformer):
        def generic_visit(self, node: ast.AST) -> Any:
            if skipper and skipper(node):
                return node
            node = super().generic_visit(node)
            return replacer(node)
    Replacer().visit(node)
    return results

def token_type_to_go_type(t: token):
    if t == token.INT:
        return GoBasicType.INT.ident
    if t == token.FLOAT:
        return GoBasicType.FLOAT64.ident
    if t == token.STRING:
        return GoBasicType.STRING.ident
    if t == token.IMAG:
        return GoBasicType.COMPLEX128.ident
    if t == token.CHAR:
        return GoBasicType.BYTE.ident
    raise ValueError(t)


def from_method(node):
    return f"from_{node.__class__.__name__}"


T = TypeVar('T')
def from_this(cls: Type[T], node) -> T:
    return getattr(cls, from_method(node))(node)

_sort_key_cache = {}
def sort_key_for_node(x_node):
    x_node_type = type(x_node)
    if sort_key := _sort_key_cache.get(str(x_node_type)):
        pass
    else:
        def sort_key(x_type):
            if n := x_type.CONVERSION_ORDER.get(x_node_type):
                return n
            return 0
        _sort_key_cache[str(x_node_type)] = sort_key
    return sort_key

def _build_x_list(x_types: list, x_name: str, nodes, **kwargs):
    li = []
    for x_node in nodes:
        method = from_method(x_node)
        errors = []
        for x_type in sorted(x_types, key=sort_key_for_node(x_node)):
            if hasattr(x_type, method):
                try:
                    result = getattr(x_type, method)(x_node, **kwargs)
                except NotImplementedError as e:
                    errors.append((x_type, e))
                    continue
                if isinstance(result, list):
                    li += result
                else:
                    li.append(result)
                break
        else:
            raise ValueError(f"No {x_name} type in {x_types} with {method}: "
                             f"\n```\n{ast.unparse(x_node) if x_node else None}\n```") from Exception(errors)
    return li

def _construct_error(exception: ast.AST):
    panic_msg = ""
    args = []
    match exception:
        case ast.Assert():
            panic_msg += "AssertionError"
            if exception.msg:
                args.append(exception.msg)
        case ast.Call(func=ast.Name(id=exception_name), args=args):
            panic_msg += exception_name
    if args:
        panic_msg += ': ' + ', '.join(["%v"] * len(args))
    panic_msg = panic_msg or "Exception"
    if args:
        fmt = Ident.from_str("fmt")
        panic_msg = fmt.sel("Errorf").call(BasicLit(Kind=token.STRING, Value=panic_msg), *build_expr_list(args))
    else:
        errors = Ident.from_str("errors")
        panic_msg = errors.sel("New").call(BasicLit(Kind=token.STRING, Value=panic_msg))
    return panic_msg

def build_expr_list(nodes, **kwargs) -> list['Expr']:
    return _build_x_list(_EXPR_TYPES, "Expr", nodes, **kwargs)


def build_stmt_list(nodes, **kwargs) -> list['Stmt']:
    return _build_x_list(_STMT_TYPES, "Stmt", nodes, **kwargs)


def build_decl_list(nodes) -> list['Decl']:
    decls = []
    global_mode = False
    for node in nodes:
        try:
            decls += _build_x_list(_DECL_TYPES, "Decl", [node], global_mode=global_mode)
        except ValueError:
            decls.append(FuncDecl.from_global_code(node))
            # From this point on, all variable assignmnts must be handled inside an init.
            global_mode = True
    return decls

import sys
import types

def exception_with_traceback():
    tb = None
    depth = 0
    while True:
        try:
            frame = sys._getframe(depth)
            depth += 1
        except ValueError as exc:
            break

        tb = types.TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)

    trace_list = traceback.format_list(traceback.extract_tb(tb))
    pretty_trace_list = []
    for t in reversed(trace_list):
        if "pytago" not in t:
            continue
        pretty_trace_list.append(t.rsplit('pytago', 1)[-1])
    return pretty_trace_list

class GoAST(ast.AST):
    CONVERSION_ORDER = {}
    STORY = []

    _prefix = "ast."

    def __init__(self, parents=None, **kwargs):
        super().__init__(**kwargs)
        self.parents = parents or []
        for field_name in self._fields:
            field = getattr(self, field_name, None)
            if isinstance(field, GoAST):
                field.parents.append(self)
        # GoAST.STORY.append(self)
        # self.STORY_INDEX = len(GoAST.STORY)
        # self.TRACE = exception_with_traceback()  # Debugging

    def remove_falsy_fields(self):
        self._fields = [f for f in self._fields if getattr(self, f, None)]

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        for field in self._fields:
            if getattr(self, field, None) != getattr(other, field, None):
                return False

        return True

    def __repr__(self):
        from pytago.go_ast import parsing
        return parsing.dump(self)


class Expr(GoAST):
    def __init__(self, *args, _type_help=None, _py_context=None, **kwargs):
        self._type_help = _type_help
        self._py_context = _py_context or {}
        super().__init__(**kwargs)

    def __or__(self, Y: 'Expr') -> 'BinaryExpr':
        """
        Shorthand way to describe the binary expression self | Y
        """
        return BinaryExpr(Op=token.OR, X=self, Y=Y)

    def __mul__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.MUL, X=self, Y=Y)

    def __add__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.ADD, X=self, Y=Y)

    def __le__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.LEQ, X=self, Y=Y)

    def __lt__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.LSS, X=self, Y=Y)

    def __ge__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.GEQ, X=self, Y=Y)

    def __gt__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.GTR, X=self, Y=Y)

    def __sub__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.SUB, X=self, Y=Y)

    def __truediv__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.QUO, X=self, Y=Y)

    def __lshift__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.SHL, X=self, Y=Y)

    def __rshift__(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.SHR, X=self, Y=Y)

    def __neg__(self) -> 'UnaryExpr':
        return UnaryExpr(Op=token.SUB, X=self)

    def or_(self, Y: 'Expr') -> 'BinaryExpr':
        """
        Shorthand way to describe the binary expression self || Y
        """
        return BinaryExpr(Op=token.LOR, X=self, Y=Y)

    def and_(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.LAND, X=self, Y=Y)

    def eql(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.EQL, X=self, Y=Y)

    def neq(self, Y: 'Expr') -> 'BinaryExpr':
        return BinaryExpr(Op=token.NEQ, X=self, Y=Y)

    def sel(self, sel, **kwargs) -> 'SelectorExpr':
        """
        Shorthand way to describe the attribute access self.{{ sel }}
        """
        return SelectorExpr(X=self, Sel=from_this(Ident, sel), **kwargs)

    def call(self, *args, **kwargs) -> 'CallExpr':
        return CallExpr(Args=list(args), Fun=self, **kwargs)

    def return_(self, **kwargs) -> 'ReturnStmt':
        return ReturnStmt(Results=[self], **kwargs)

    def receive(self, **kwargs) -> 'UnaryExpr':
        return UnaryExpr(Op=token.ARROW, X=self, **kwargs)

    def send(self, value: 'Expr', **kwargs):
        return SendStmt(Chan=self, Value=value, **kwargs)

    def not_(self, **kwargs):
        return UnaryExpr(Op=token.NOT, X=self)

    def stmt(self, **kwargs):
        return ExprStmt(X=self, **kwargs)

    def chan(self, dir=3, **kwargs):
        return ChanType(Value=self, Dir=dir, **kwargs)

    def defer(self, **kwargs):
        return DeferStmt(Call=self, **kwargs)

    def go(self, **kwargs):
        return GoStmt(Call=self, **kwargs)

    def composite_lit_type(self, **kwargs):
        return CompositeLit(Type=self, **kwargs)

    def ref(self, **kwargs):
        return UnaryExpr(X=self, Op=token.AND, **kwargs)

    def deref(self, **kwargs):
        return StarExpr(X=self, **kwargs)

    def if_(self, body: List['Stmt'], else_=None, **kwargs):
        return IfStmt(Cond=self, Body=BlockStmt(List=body.copy()), Else=else_, **kwargs)

    def assign(self, *expr: 'Expr', tok=token.DEFINE, **kwargs) -> 'AssignStmt':
        assert expr
        return AssignStmt(Lhs=[self], Rhs=list(expr), Tok=tok, **kwargs)

    @property
    def basic_type(self) -> Optional[GoBasicType]:
        try:
            return GoBasicType(self.Name)
        except (AttributeError, ValueError):
            return None

    @property
    def is_basic_type(self):
        return self.basic_type is not None

    @property
    def is_unsigned_integer_type(self):
        return bool(self.basic_type) and self.basic_type.is_unsigned_integer

    @property
    def is_signed_integer_type(self):
        return bool(self.basic_type) and self.basic_type.is_signed_integer

    @property
    def is_integer_type(self):
        return bool(self.basic_type) and self.basic_type.is_integer

    @property
    def is_float_type(self):
        return bool(self.basic_type) and self.basic_type.is_float

    @property
    def is_complex_type(self):
        return bool(self.basic_type) and self.basic_type.is_complex

    @property
    def is_numeric_type(self):
        return bool(self.basic_type) and self.basic_type.is_numeric

    @property
    def is_type_with_length(self):
        match self:
            case Ident(Name=GoBasicType.STRING.value) | ArrayType() | MapType():
                return True
        return False

    @property
    def min_val(self):
        if self.is_numeric_type:
            # https://stackoverflow.com/questions/6878590/the-maximum-value-for-an-int-type-in-go
            if self.is_unsigned_integer_type:
                return BasicLit.from_int(0)
            if self.basic_type == GoBasicType.INT:
                return (BasicLit.from_int(1) << Ident("bits").sel("UintSize")) / -BasicLit.from_int(2)
            return Ident("math").sel(f"Min{self.basic_type.value.title()}")
        if self.basic_type == GoBasicType.STRING:
            return BasicLit(token.STRING, "")

    @property
    def max_val(self):
        if self.is_numeric_type:
            # https://stackoverflow.com/questions/6878590/the-maximum-value-for-an-int-type-in-go
            if self.basic_type == GoBasicType.UINT:
                return (BasicLit.from_int(1) << Ident("bits").sel("UintSize")) - BasicLit.from_int(1)
            if self.basic_type == GoBasicType.INT:
                return (BasicLit.from_int(1) << Ident("bits").sel("UintSize")) / BasicLit.from_int(2) - BasicLit.from_int(1)
            return Ident("math").sel(f"Max{self.basic_type.value.title()}")

    def cast(self, type_1: 'Expr', type_2: 'Expr') -> 'Expr':
        if type_1 == type_2:
            return self

        if isinstance(self, BasicLit):
            # We don't need to cast literals just to add them to use them as another type
            if type_1.is_numeric_type and type_2.is_numeric_type:
                return self

        match type_1, type_2:
            case Ident(Name=GoBasicType.BOOL.value), x if x.is_numeric_type:
                return FuncLit(
                    Type=FuncType(Results=FieldList(List=[Field(Type=type_2)])),
                    Body=BlockStmt(List=[
                        self.if_([BasicLit.from_int(1).return_()]),
                        BasicLit.from_int(0).return_()
                    ])
                ).call()
            case x, Ident(Name=GoBasicType.BOOL.value) if x.is_type_with_length:
                return Ident("len").call(self).neq(BasicLit.from_int(0))
            case x, Ident(Name=GoBasicType.BOOL.value) if x.is_numeric_type:
                return self.neq(BasicLit.from_int(0))
        return type_2.call(self)

    def __getitem__(self, item):
        # Convenience function to let me cleanly represent subscripts in transformation
        if isinstance(item, slice):
            raise NotImplementedError("This shortcut isn't implemented for slices")
        if isinstance(item, bool):
            return IndexExpr(X=self, Index=Ident.from_str(str(item).lower()))
        if isinstance(item, int):
            return IndexExpr(X=self, Index=BasicLit.from_int(item))
        if isinstance(item, str):
            return IndexExpr(X=self, Index=BasicLit(Value=item, Kind=token.STRING))
        return IndexExpr(X=self, Index=item)

    def _type(self, scope: Optional['Scope'] = None, interface_ok=False, **kwargs):
        return self._type_help


class Stmt(GoAST):
    ...


class Decl(GoAST):
    ...


class ArrayType(Expr):
    """An ArrayType node represents an array or slice type."""
    _fields = ('Elt', 'Len')
    """element type"""
    Elt: Expr
    """position of '['"""
    Lbrack: int
    """Ellipsis node for [...]T array types, nil for slice types"""
    Len: Expr

    def __init__(self,
                 Elt: Expr = None,
                 Lbrack: int = 0,
                 Len: Expr = None,
                 **kwargs) -> None:
        self.Elt = Elt or InterfaceType()
        self.Lbrack = Lbrack
        self.Len = Len
        super().__init__(**kwargs)

    @classmethod
    def from_NoneType(cls, node: None, **kwargs):
        return cls(InterfaceType(), **kwargs)

    @classmethod
    def from_BasicLit(cls, node: 'BasicLit', **kwargs):
        return cls(token_type_to_go_type(node.Kind), 0, None, **kwargs)

    @classmethod
    def from_Ident(cls, node: 'Ident', **kwargs):
        obj = cls(node, **kwargs)
        return obj


class AssignStmt(Stmt):
    _fields = ['Lhs', 'Rhs', 'Tok']

    """An AssignStmt node represents an assignment or a short variable declaration."""
    Lhs: List[Expr]
    Rhs: List[Expr]
    """assignment token, DEFINE"""
    Tok: token
    """position of Tok"""
    TokPos: int

    def __init__(self,
                 Lhs: List[Expr] = None,
                 Rhs: List[Expr] = None,
                 Tok: token = None,
                 TokPos: int = 0,
                 **kwargs) -> None:
        self.Lhs = Lhs or []
        set_list_type(self.Lhs, "ast.Expr")
        self.Rhs = Rhs or []
        set_list_type(self.Rhs, "ast.Expr")
        self.Tok = Tok or token.ASSIGN
        self.TokPos = TokPos
        super().__init__(**kwargs)

    @classmethod
    def from_Assign(cls, node: ast.Assign, **kwargs):
        _rhs = build_expr_list([node.value])

        # Ugly code to try and spot unpacking into a tuple
        if len(_rhs) == 1 \
                and (len(node.targets) > 1 or (len(node.targets) == 1 and hasattr(node.targets[0], "elts"))) \
                and hasattr(_rhs[0], "Elts"):
            rhs = _rhs[0].Elts
        else:
            rhs = _rhs
        ctx = {}
        for rh_expr in rhs:
            ctx.update(rh_expr._py_context)
        _lhs = build_expr_list(node.targets, _type_help=rhs[0]._type(), _py_context=ctx)
        lhs = []
        for l in _lhs:
            if isinstance(l, CompositeLit):
                lhs += l.Elts
            else:
                lhs.append(l)

        return cls(lhs, rhs, token.DEFINE, 0, **kwargs)

    @classmethod
    def from_withitem(cls, node: ast.withitem, **kwargs):
        rhs = build_expr_list([node.context_expr])
        ctx = {}
        for rh_expr in rhs:
            ctx.update(rh_expr._py_context)
        lhs = build_expr_list([node.optional_vars], _type_help=rhs[0]._type(), _py_context=ctx)
        return cls(lhs, rhs, token.DEFINE, 0, **kwargs)

    @classmethod
    def from_AugAssign(cls, node: ast.AugAssign, **kwargs):
        lhs = build_expr_list([node.target])
        rhs = build_expr_list([node.value])

        match node.op:
            case ast.Add(): op = token.ADD_ASSIGN
            case ast.Sub(): op = token.SUB_ASSIGN
            case ast.Mult(): op = token.MUL_ASSIGN
            case ast.Div(): op = token.QUO_ASSIGN
            case ast.Mod(): op = token.REM_ASSIGN
            case ast.BitAnd(): op = token.AND_ASSIGN
            case ast.BitOr(): op = token.OR_ASSIGN
            case ast.BitXor(): op = token.XOR_ASSIGN
            case ast.LShift(): op = token.SHL_ASSIGN
            case ast.RShift(): op = token.SHR_ASSIGN
            # case ast.FloorDiv() | ast.Pow():  # TODO
            #     ...
            case ast.MatMult():
                # Special case: Way to express an assignment to a reference.
                lhs = [StarExpr(X=x) for x in lhs]
                op = token.ASSIGN
            case _:
                raise NotImplementedError(node.op)
        return cls(lhs, rhs, op, **kwargs)

    @classmethod
    def from_FunctionDef(cls, node: ast.FunctionDef, **kwargs):
        rhs = build_expr_list([node])
        lhs = build_expr_list([node.name], _type_help=rhs[0]._type())
        return cls(lhs, rhs, token.DEFINE, **kwargs)

    @classmethod
    def from_NamedExpr(cls, node: ast.NamedExpr, **kwargs):
        lhs = build_expr_list([node.target])
        rhs = build_expr_list([node.value])
        return cls(lhs, rhs, token.DEFINE, **kwargs)


class BadDecl(Decl):
    """A BadDecl node is a placeholder for declarations containing syntax errors for which no
    correct declaration nodes can be created.
    """
    _fields = tuple()
    From: int
    To: int

    def __init__(self,
                 From: int = 0,
                 To: int = 0,
                 **kwargs) -> None:
        self.From = From
        self.To = To
        super().__init__(**kwargs)


class BadExpr(Expr):
    """A BadExpr node is a placeholder for expressions containing syntax errors for which no
    correct expression nodes can be created.
    """
    _fields = tuple()
    From: int
    To: int

    def __init__(self,
                 From: int = 0,
                 To: int = 0,
                 **kwargs) -> None:
        self.From = From
        self.To = To
        super().__init__(**kwargs)

    @classmethod
    def from_NamedExpr(cls, node: ast.NamedExpr, **kwargs):
        # A transformer can go in and add this to the Init of if statements and such
        return cls(_py_context={"NamedExpr": from_this(AssignStmt, node)}, **kwargs)


class BadStmt(Stmt):
    """A BadStmt node is a placeholder for statements containing syntax errors for which no
    correct statement nodes can be created.
    """
    _fields = tuple()
    From: int
    To: int
    _pyAST: Optional[ast.AST]

    def __init__(self,
                 From: int = 0,
                 To: int = 0,
                 _pyAST = None,
                 **kwargs) -> None:
        self.From = From
        self.To = To
        self._pyAST = _pyAST  # Used by transformers in postprocessing stage
        super().__init__(**kwargs)


    @classmethod
    def from_Global(cls, node: ast.Global, **kwargs):
        return cls(_pyAST=node, **kwargs)

    @classmethod
    def from_Nonlocal(cls, node: ast.Nonlocal, **kwargs):
        return cls(_pyAST=node, **kwargs)

    @classmethod
    def from_Import(cls, node: ast.Import, **kwargs):
        return cls(_pyAST=node, **kwargs)  # TODO: Bubble these to top

    @classmethod
    def from_ImportFrom(cls, node: ast.ImportFrom, **kwargs):
        return cls(_pyAST=node, **kwargs)  # TODO: Bubble these to top

    @classmethod
    def from_ClassDef(cls, node: ast.ClassDef, **kwargs):
        # decls = from_this(GenDecl, node)
        return cls(_pyAST=node, **kwargs)


class BasicLit(Expr):
    """A BasicLit node represents a literal of basic type.

    field tag; or nil

    import path
    """
    _fields = ('Kind', 'Value')
    """token.INT, token.FLOAT, token.IMAG, token.CHAR, or token.STRING"""
    Kind: token
    """literal string; e.g. 42, 0x7f, 3.14, 1e-9, 2.4i, 'a', '⧵x7f', 'foo' or '⧵m⧵n⧵o'"""
    Value: str
    """literal position"""
    ValuePos: int

    def __init__(self,
                 Kind: token = None,
                 Value: str = None,
                 ValuePos: int = 0,
                 **kwargs) -> None:
        self.Kind = Kind
        self.Value = json.dumps(Value, ensure_ascii=False)
        self.ValuePos = ValuePos
        super().__init__(**kwargs)

    @classmethod
    def from_Constant(cls, node: ast.Constant, **kwargs):
        return cls.from_Constant_value(node.value, **kwargs)

    @classmethod
    def from_Constant_value(cls, value, **kwargs):
        t = type(value)
        if t == int:
            kind = token.INT
        elif t == float:
            kind = token.FLOAT
        elif t == str:
            kind = token.STRING
        elif t == complex:
            val = cls.from_value(f"{value.imag}i", token.IMAG, **kwargs)
            if value.real:
                # TODO: Not a basic lit in this case, a bit smelly
                val = cls.from_Constant_value(value.real, **kwargs) + val
            return val
        else:
            raise NotImplementedError(value)
        return cls(kind, value, **kwargs)

    @classmethod
    def from_int(cls, node: int, **kwargs):
        return cls(token.INT, node, 0, **kwargs)

    @classmethod
    def from_value(cls, node: Any, t: token, **kwargs):
        """
        Hack because I decided the constructor should json.dumps everything by default,
        so now I need a way around that. Cleaner to probably stop doing that and delete this method.
        """
        obj = cls(t, None, **kwargs)
        obj.Value = node
        return obj


    def _type(self, scope: Optional['Scope']=None, **kwargs):
        return token_type_to_go_type(self.Kind) or super()._type(scope, **kwargs)


class BinaryExpr(Expr):
    """A BinaryExpr node represents a binary expression."""
    _fields = ("Op", "X", "Y")
    """operator"""
    Op: token
    """position of Op"""
    OpPos: int
    """left operand"""
    X: Expr
    """right operand"""
    Y: Expr

    def __init__(self,
                 Op: token = None,
                 OpPos: int = 0,
                 X: Expr = None,
                 Y: Expr = None,
                 **kwargs) -> None:
        # Quality of life
        if isinstance(X, int):
            X = BasicLit.from_int(X)
        if isinstance(Y, int):
            Y = BasicLit.from_int(Y)

        self.Op = Op
        self.OpPos = OpPos
        self.X = X
        self.Y = Y
        super().__init__(**kwargs)

    @classmethod
    def from_Compare(cls, node: ast.Compare, **kwargs):
        py_op = node.ops[0]
        node_left = node.left
        node_right = node.comparators[0]
        expr = cls.from_left_op_right(node_left, py_op, node_right, **kwargs)
        py_op_remaining = node.ops[1:]
        py_op_remaining.reverse()
        node_right_remaining = node.comparators[1:]
        node_right_remaining.reverse()
        while py_op_remaining and node_right_remaining:
            py_op = py_op_remaining.pop()
            node_right = node_right_remaining.pop()
            expr = expr.and_(cls.from_left_op_right(expr.Y, py_op, node_right, **kwargs))
        return expr

    @classmethod
    def from_left_op_right(cls, node_left, py_op, node_right, **kwargs):
        match py_op:
            case ast.Gt():
                op = token.GTR
            case ast.GtE():
                op = token.GEQ
            case ast.Lt():
                op = token.LSS
            case ast.LtE():
                op = token.LEQ
            case ast.Eq():
                op = token.EQL
            case ast.NotEq():
                op = token.NEQ
            case ast.Is():
                op = token.PLACEHOLDER_IS
            case ast.IsNot():
                op = token.PLACEHOLDER_IS_NOT
            case ast.In():
                op = token.PLACEHOLDER_IN
            case ast.NotIn():
                op = token.PLACEHOLDER_NOT_IN
            case _:
                raise NotImplementedError(f"Unimplemented comparator: {py_op}")
        X = node_left if isinstance(node_left, Expr) else build_expr_list([node_left])[0]
        Y = node_right if isinstance(node_right, Expr) else build_expr_list([node_right])[0]
        expr = cls(op, 0, X, Y, **kwargs)
        return expr

    @classmethod
    def from_left_boolop_right(cls, node_left, py_op, node_right, **kwargs):
        match py_op:
            case ast.And():
                op = token.LAND
            case ast.Or():
                op = token.LOR
            case _:
                raise NotImplementedError(f"Unimplemented boolop: {py_op}")
        X = node_left if isinstance(node_left, Expr) else build_expr_list([node_left])[0]
        Y = node_right if isinstance(node_right, Expr) else build_expr_list([node_right])[0]
        expr = cls(op, 0, X, Y, **kwargs)
        return expr

    @classmethod
    def from_BoolOp(cls, node: ast.BoolOp, **kwargs):
        py_op = node.op
        node_left = node.values[0]
        node_right = node.values[1]
        expr = cls.from_left_boolop_right(node_left, py_op, node_right, **kwargs)
        py_op_remaining = [py_op] * (len(node.values) - 2)
        py_op_remaining.reverse()
        node_right_remaining = node.values[2:]
        node_right_remaining.reverse()
        while py_op_remaining and node_right_remaining:
            py_op = py_op_remaining.pop()
            node_right = node_right_remaining.pop()
            expr = expr.and_(cls.from_left_boolop_right(expr.Y, py_op, node_right, **kwargs))
        return expr

    @classmethod
    def from_BinOp(cls, node: ast.BinOp, **kwargs):
        py_op = node.op
        match py_op:
            case ast.Add(): op = token.ADD
            case ast.Sub(): op = token.SUB
            case ast.Mult(): op = token.MUL
            case ast.Div(): op = token.QUO
            case ast.Mod(): op = token.REM
            case ast.And(): op = token.LAND
            case ast.BitAnd(): op = token.AND
            case ast.Or(): op = token.LOR
            case ast.BitOr(): op = token.OR
            case ast.BitXor(): op = token.XOR
            case ast.LShift(): op = token.SHL
            case ast.RShift(): op = token.SHR
            case ast.Pow(): op = token.PLACEHOLDER_POW
            case ast.FloorDiv(): op = token.PLACEHOLDER_FLOOR_DIV
            # case ...:
            #     op = token.AND_NOT
            case _:
                raise NotImplementedError(f"Unimplemented binop: {py_op}")
        X = build_expr_list([node.left])[0]
        Y = build_expr_list([node.right])[0]
        return cls(op, 0, X, Y, **kwargs)

    def _type(self, scope: Optional['Scope'] = None, **kwargs):
        if self.Op in COMPARISON_OPS or self.Op in BOOL_OPS:
            return GoBasicType.BOOL.ident
        if scope:
            return scope._get_type(self.X, **kwargs) or scope._get_type(self.Y, **kwargs) or super()._type(scope, **kwargs)
        return self.X._type(**kwargs) or self.Y._type(**kwargs) or super()._type(**kwargs)


class BlockStmt(Stmt):
    """A BlockStmt node represents a braced statement list.

    function body; or nil for external (non-Go) function

    function body

    CommClauses only

    CaseClauses only
    """
    _fields = ("List",)
    """position of '{'"""
    Lbrace: int
    List: List[Stmt]
    """position of '}', if any (may be absent due to syntax error)"""
    Rbrace: int

    def __init__(self,
                 Lbrace: int = 0,
                 List: List[Stmt] = None,
                 Rbrace: int = 0,
                 **kwargs) -> None:
        self.Lbrace = Lbrace
        self.List = List or []
        set_list_type(self.List, "ast.Stmt")
        self.Rbrace = Rbrace
        super().__init__(**kwargs)

    @classmethod
    def from_list(cls, node_list, **kwargs):
        stmts = build_stmt_list(node_list)
        return cls(0, stmts, 0, **kwargs)


class Object(GoAST):
    """denoted object; or nil

    Objects An Object describes a named language entity such as a package, constant, type,
    variable, function (incl. methods), or label.

    The Data fields index object-specific data:
    Kind    Data type         Data value
    Pkg     *Scope            package scope
    Con     int               iota for the respective declaration
    """
    _fields = ("Data", "Decl", "Kind", "Name", "Type")
    """object-specific data; or nil"""
    Data: Expr
    """corresponding Field, XxxSpec, FuncDecl, LabeledStmt, AssignStmt, Scope; or nil"""
    Decl: Decl
    Kind: ObjKind
    """declared name"""
    Name: str
    """placeholder for type information; may be nil"""
    Type: Expr

    def __init__(self,
                 Data: Expr = None,
                 Decl: Decl = None,
                 Kind: ObjKind = None,
                 Name: str = None,
                 Type: Expr = None,
                 _py_context: dict = None,
                 **kwargs) -> None:
        self.Data = Data
        self.Decl = Decl
        self.Kind = Kind
        self.Name = Name
        self.Type = Type
        self._py_context = _py_context or {}
        super().__init__(**kwargs)


class Ident(Expr):
    """label name; or nil

    local package name (including '.'); or nil

    package name

    function/method name

    An Ident node represents an identifier.

    field selector

    type name
    """
    _fields = ("Name",)
    """identifier name"""
    Name: str
    """identifier position"""
    NamePos: int
    """denoted object; or nil"""
    Obj: Object

    def __init__(self,
                 Name: str = None,
                 NamePos: int = 0,
                 Obj: Object = None,
                 **kwargs) -> None:
        self.Name = Name
        self.NamePos = NamePos
        self.Obj = Obj

        super().__init__(**kwargs)

    @classmethod
    def from_Constant(cls, node: ast.Constant, **kwargs):
        match node.value:
            case bool():
               return cls.from_str(str(node.value).lower(), **kwargs)
            case None:
                return cls.from_str("nil", **kwargs)
        raise NotImplementedError(node)

    @classmethod
    def from_Name(cls, name: ast.Name, **kwargs):
        match name.id:
            case 'PYTAGO_EMPTY_STRUCT':
                return CompositeLit(Type=StructType(), **kwargs)
        return cls.from_str(name.id, **kwargs)

    @classmethod
    def from_str(cls, name: str, **kwargs):
        return cls(name, 0, None, **kwargs)

    def field(self, type_: Optional[Expr]=None, named=True, **kwargs) -> 'Field':
        return Field(
            Names=[self] if named else None,
            Type=type_ or self._type(),
            **kwargs
        )

    def fieldlist(self, type_: Optional[Expr] = None, named=True, **kwargs) -> 'FieldList':
        return FieldList(List=[self.field(type_, named)], **kwargs)

class BranchStmt(Stmt):
    """A BranchStmt node represents a break, continue, goto, or fallthrough statement."""
    _fields = ("Label", "Tok")
    """label name; or nil"""
    Label: Ident
    """keyword token (BREAK, CONTINUE, GOTO, FALLTHROUGH)"""
    Tok: token
    """position of Tok"""
    TokPos: int

    def __init__(self,
                 Label: Ident = None,
                 Tok: token = None,
                 TokPos: int = 0,
                 **kwargs) -> None:
        self.Label = Label
        self.Tok = Tok
        self.TokPos = TokPos
        super().__init__(**kwargs)

    @classmethod
    def from_Continue(cls, node: ast.Continue):
        return cls(Tok=token.CONTINUE)

    @classmethod
    def from_Break(cls, node: ast.Break):
        return cls(Tok=token.BREAK)



class CallExpr(Expr):
    """A CallExpr node represents an expression followed by an argument list."""
    _fields = ('Args', 'Ellipsis', 'Fun')
    """function arguments; or nil"""
    Args: List[Expr]
    """position of '...' (token.NoPos if there is no '...')"""
    Ellipsis: int
    """function expression"""
    Fun: Expr
    """position of '('"""
    Lparen: int
    """position of ')'"""
    Rparen: int

    def __init__(self,
                 Args: List[Expr] = None,
                 Ellipsis: int = 0,
                 Fun: Expr = None,
                 Lparen: int = 0,
                 Rparen: int = 0,
                 **kwargs) -> None:
        self.Args = Args or []
        set_list_type(self.Args, "ast.Expr")
        self.Ellipsis = Ellipsis
        self.Fun = Fun
        self.Lparen = Lparen
        self.Rparen = Rparen
        super().__init__(**kwargs)

    @classmethod
    def from_Call(cls, node: ast.Call, _py_context=None):
        try:
            py_nosnippet = node.func.py_nosnippet
        except AttributeError:
            py_nosnippet = False
        match node.func:
            case ast.Name(id='PYTAGO_RUNE'):
                match node.args:
                    case [ast.Constant(value=v)] if isinstance(v, str) and len(v) == 1:
                        bl = BasicLit.from_value(node="'" + json.dumps(v)[1:-1] + "'", t=token.CHAR)
                        return bl
                    case _:
                        raise NotImplementedError()
            case ast.Call(ast.Name(id='PYTAGO_NOSNIPPET')):
                match node.func.args:
                    case [ast.AST() as x]:
                        node.func = x
                        x.py_nosnippet = True
                        py_nosnippet = True
                    case _:
                        raise NotImplementedError()

        if not py_nosnippet:
            f = find_call_funclit(node)
            if f:
                return f

        _type_help = None
        match node:
            case ast.Call(func=ast.Name(id=x), args=[]):
                match x:
                    case 'set' | 'frozenset':
                        return CompositeLit.from_Set(ast.Set(elts=[]))
                    case 'list' | 'dict' | 'tuple' | 'int' | 'float' | 'bool' | 'complex' | 'string' | 'bytes':
                        py_value = ast.parse(repr(__builtins__[x]()))
                        expr = build_expr_list(py_value.body)[0]
                        return expr
                    case 'bytearray':
                        py_value = ast.parse(repr(b''))  # Preferring bytes form for now
                        expr = build_expr_list(py_value.body)[0]
                        return expr

        ellipsis = 0
        match node:
            # Special case to calls to the open function
            case ast.Call(func=ast.Name(id="isinstance"), args=[__expr, __types]):
                _expr = build_expr_list([__expr])[0]
                try:
                    _types = [_type_annotation_to_go_type(x) for x in __types.elts]
                except AttributeError:
                    _types = [_type_annotation_to_go_type(__types)]
                return FuncLit(
                    Results=FieldList(List=[Field(Type=Ident("bool"))]),
                    Body=BlockStmt(List=[
                        TypeSwitchStmt(Assign=TypeAssertExpr(X=_expr).stmt(), Body=BlockStmt(List=[
                            CaseClause(List=_types, Body=[
                                Ident("true").return_()
                            ]),
                        ])),
                        Ident("false").return_()
                    ])
                ).call()
            case ast.Call(func=ast.Name(id='open'), args=[filename_expr, ast.Constant(value=mode)]):
                args, fun, _py_context, _type_help = cls._open_call_helper(_py_context, _type_help, filename_expr, mode)
            case _:
                args = []
                for arg_node in node.args:
                    if isinstance(arg_node, ast.Starred):
                        ellipsis = 1  # TODO: These can only appear at the end of the call and there can only be one
                        arg_node = arg_node.value
                    args += build_expr_list([arg_node])

                # Must be dealt with by a transformer later
                kwargs = build_expr_list([x.value for x in node.keywords])
                for kwarg, kw in zip(kwargs, node.keywords):
                    kwarg._py_context.update({"keyword": kw.arg})
                args += kwargs
                fun = build_expr_list([node.func])[0]
        return cls(Args=args, Fun=fun, Ellipsis=ellipsis, _type_help=_type_help, _py_context=_py_context)

    @classmethod
    def from_IfExp(cls, node: ast.IfExp, **kwargs):
        if not node.orelse:
            raise NotImplementedError(node, "Cannot have a function with no return")
        if_ = IfStmt.from_IfExp(node, action=lambda x: ReturnStmt(Results=[x]))
        t = if_.Body.List[-1].Results[0]._type()
        else_ = if_.Else.List
        if_.Else = None
        if t is None:
            t = else_[-1].Results[0]._type()

        fun = FuncLit(
            Type=FuncType(
                Results=FieldList(List=[Field(Type=t)])
            ),
            Body=BlockStmt(List=[
                if_,
                *else_
            ])
        )
        return fun.call(**kwargs)

    @classmethod
    def from_ListComp_or_GeneratorExp(cls, node: ast.ListComp | ast.GeneratorExp, **kwargs):
        gen_mode = isinstance(node, ast.GeneratorExp)

        elt = build_expr_list([node.elt])[0]
        comps = build_stmt_list(node.generators)
        elts = Ident('yield' if gen_mode else 'elts')
        wait = Ident('wait')

        def inner_body(b: BlockStmt):
            while b.List:
                b = b.List[0].Body
            return b

        comp: RangeStmt = comps.pop()

        if gen_mode:
            inner_body(comp.Body).List += [elts.send(elt), wait.receive().stmt()]
        else:
            inner_body(comp.Body).List.append(
                elts.assign(Ident("append").call(elts, elt), tok=token.ASSIGN)
            )
        while comps:
            inner_body(comps[-1].Body).List.append(comp)
            comp = comps.pop()

        e_type = elt._type() or InterfaceType(_py_context={"elts": [elt]})
        if gen_mode:
            r_type = FieldList(List=[Field(Type=e_type)])
        else:
            r_type = elts.fieldlist(type_=ArrayType(Elt=e_type))
        fun = FuncLit(
            Type=FuncType(
                Results=r_type
            ),
            Body=BlockStmt(List=[
                comp,
            ] + ([] if gen_mode else [ReturnStmt()])))
        return fun.call(**kwargs)

    @classmethod
    def from_ListComp(cls, node: ast.ListComp, **kwargs):
        return cls.from_ListComp_or_GeneratorExp(node, **kwargs)

    @classmethod
    def from_GeneratorExp(cls, node: ast.GeneratorExp, **kwargs):
        return cls.from_ListComp_or_GeneratorExp(node, **kwargs)

    @classmethod
    def from_DictComp_or_SetComp(cls, node: ast.SetComp | ast.DictComp, **kwargs):
        set_mode = isinstance(node, ast.SetComp)
        key = build_expr_list([node.elt if set_mode else node.key])[0]
        value = CompositeLit(Type=StructType()) if set_mode else build_expr_list([node.value])[0]
        comps = build_stmt_list(node.generators)
        d = Ident('s') if set_mode else Ident('d')

        def inner_body(b: BlockStmt):
            while b.List:
                b = b.List[0].Body
            return b

        comp: RangeStmt = comps.pop()
        inner_body(comp.Body).List.append(
            d[key].assign(value, tok=token.ASSIGN)
        )
        while comps:
            inner_body(comps[-1].Body).List.append(comp)
            comp = comps.pop()

        key_type = key._type() or InterfaceType(_py_context={"elts": [key]})
        value_type = value._type() or InterfaceType(_py_context={"elts": [value]})
        fun = FuncLit(
            Type=FuncType(
                Results=d.fieldlist(type_=MapType(Key=key_type, Value=value_type))
            ),
            Body=BlockStmt(List=[
                comp,
                ReturnStmt()
            ]))
        return fun.call(**kwargs)

    @classmethod
    def from_DictComp(cls, node: ast.DictComp, **kwargs):
        return cls.from_DictComp_or_SetComp(node, **kwargs)

    @classmethod
    def from_SetComp(cls, node: ast.SetComp, **kwargs):
        return cls.from_DictComp_or_SetComp(node, **kwargs)

    @classmethod
    def _open_call_helper(cls, _py_context, _type_help, filename_expr, mode):
        args = build_expr_list([filename_expr])
        os = Ident.from_str('os')
        perm = os.sel('O_RDONLY')
        _py_context = {'text_mode': 'b' not in mode}  # TODO: Care about text mode
        mode = mode.replace('b', '').replace('t', '')
        mode = ''.join(sorted(mode, reverse=True))
        match mode:
            case 'r':
                perm = os.sel('O_RDONLY')
            case 'r+':
                perm = os.sel('O_RDWR')
            case 'w':
                perm = os.sel('O_WRONLY') | os.sel('O_TRUNC')
            case 'w+':
                perm = os.sel('O_RDWR') | os.sel('O_TRUNC') | os.sel('O_CREATE')
            case 'a':
                perm = os.sel('O_WRONLY') | os.sel('O_APPEND') | os.sel('O_CREATE')
            case 'a+':
                perm = os.sel('O_RDWR') | os.sel('O_APPEND') | os.sel('O_CREATE')
            case 'x':
                perm = os.sel('O_WRONLY') | os.sel('O_EXCL') | os.sel('O_CREATE')
            case 'x+':
                perm = os.sel('O_RDWR') | os.sel('O_EXCL') | os.sel('O_CREATE')
        args += [perm, BasicLit.from_value("0o777", token.INT)]
        fun = os.sel("OpenFile")
        _type_help = StarExpr(X=os.sel("File"))
        return args, fun, _py_context, _type_help

    @classmethod
    def from_JoinedStr(cls, node: ast.JoinedStr, **kwargs):
        template_string = ""
        value_elements: list[KeyValueExpr] = []
        used_keys = set()
        expr_num = 1
        for value in node.values:
            match value:
                case ast.Constant():
                    template_string += value.value
                case ast.FormattedValue():
                    # TODO: Technically, there's still a name collision here if a value like "expr1" exists later
                    fval = build_expr_list([value.value])[0]
                    if isinstance(fval, Ident):
                        key = fval.Name
                    else:
                        key = f"expr{expr_num}"
                        while key in used_keys:
                            expr_num += 1
                            f"expr{expr_num}"
                    template_string += "{{.%s}}" % key
                    used_keys.add(key)
                    value_elements.append(KeyValueExpr(Key=BasicLit(token.STRING, key), Value=fval))
                case _:
                    raise NotImplementedError(value)
        return ast_snippets.fstring(template_string, value_elements, **kwargs)

    @classmethod
    def from_Constant(cls, node: ast.Constant, **kwargs):
        match node.value:
            case bytes():
                return cls(
                    Fun=ArrayType(Elt=GoBasicType.BYTE.ident),
                    Args=[BasicLit(Kind=token.STRING, Value=node.value.decode())], **kwargs)
            case _:
                raise NotImplementedError(node, type(node.value))

    @classmethod
    def from_Delete(cls, node: ast.Delete):
        t = node.targets[0]  # TODO: Support multiple deletes and slices

        if not hasattr(t, "slice"):
            rest = []
        elif hasattr(t.slice, "value"):
            rest = build_expr_list([t.slice.value])
        else:
            rest = build_expr_list([t.slice])

        return cls(Fun=Ident.from_str("delete"), Args=build_expr_list([t.value]) + rest)

    def _type(self, scope: Optional['Scope']=None, **kwargs):
        match self.Fun:
            # Maps and arrays
            case MapType() | ArrayType():
                return self.Fun or super()._type(scope, **kwargs)
            # Function literals
            case FuncLit():
                fun_type = self.Fun._type(scope, **kwargs)
                match fun_type:
                    case FuncType(Results=FieldList(List=[one])):
                        return one.Type
                    case FuncType(Results=FieldList(List=[one, *others])):
                        return one.Type, *[other.Type for other in others]
            case Ident(Name='append'):
                element_type = self.Args[1]._type(scope, **kwargs)
                if element_type:
                    return ArrayType(Elt=element_type, _py_context=element_type._py_context)

            # Probably better ways to handle this, but let's add some types for expressions from py_snippets
            case SelectorExpr(X=x, Sel=sel):
                match x, sel:
                    case Ident(Name=_x), Ident(Name=_y):
                        dotted = _x + "." + _y
                        match dotted:
                            case "rand.Float64":
                                return GoBasicType.FLOAT64.ident
                            case "rand.Intn":
                                return GoBasicType.INT.ident

            # Basic types
            case Ident(Name=x):
                try:
                    return GoBasicType(x).ident or super()._type(scope, **kwargs)
                except ValueError:
                    pass

        if kwargs.get("interface_ok"):
            return InterfaceType(_py_context={"elts": [self]})

        return super()._type(scope, **kwargs)


class CaseClause(Stmt):
    """A CaseClause represents a case of an expression or type switch statement."""
    _fields = ("Body", "List")
    """statement list; or nil"""
    Body: List[Stmt]
    """position of 'case' or 'default' keyword"""
    Case: int
    """position of ':'"""
    Colon: int
    """list of expressions or types; nil means default case"""
    List: List[Expr]

    def __init__(self,
                 Body: List[Stmt] = None,
                 Case: int = 0,
                 Colon: int = 0,
                 List: List[Expr] = None,
                 **kwargs) -> None:
        self.Body = Body or []
        set_list_type(self.Body, "ast.Stmt")
        self.Case = Case
        self.Colon = Colon
        self.List = List or []
        set_list_type(self.List, "ast.Expr")
        super().__init__(**kwargs)

    @classmethod
    def from_match_case(cls, case: ast.match_case, **kwargs):
        match case.pattern:
            case ast.MatchValue():
                expr_list = build_expr_list([case.pattern.value], **kwargs)
            case ast.MatchAs(name=name) if name is None:
                expr_list = []  # Default
            case _:
                raise NotImplementedError()
        return cls(
            Body=build_stmt_list(case.body, **kwargs),
            List=expr_list
        )


class ChanType(Expr):
    """A ChanType node represents a channel type."""
    _fields = ("Dir", "Value")
    """position of '<-' (token.NoPos if there is no '<-')"""
    Arrow: int
    """position of 'chan' keyword or '<-' (whichever comes first)"""
    Begin: int
    """channel direction"""
    Dir: int
    """value type"""
    Value: Expr

    def __init__(self,
                 Arrow: int = 0,
                 Begin: int = 0,
                 Dir: int = 0,
                 Value: Expr = None,
                 **kwargs) -> None:
        self.Arrow = Arrow
        self.Begin = Begin
        self.Dir = Dir
        self.Value = Value or InterfaceType()
        super().__init__(**kwargs)


class CommClause(GoAST):
    """A CommClause node represents a case of a select statement."""
    _fields = ("Body", "Comm")
    """statement list; or nil"""
    Body: List[Expr]
    """position of 'case' or 'default' keyword"""
    Case: int
    """position of ':'"""
    Colon: int
    """send or receive statement; nil means default case"""
    Comm: Expr

    def __init__(self,
                 Body: List[Expr] = None,
                 Case: int = 0,
                 Colon: int = 0,
                 Comm: Expr = None,
                 **kwargs) -> None:
        self.Body = Body or []
        self.Case = Case
        self.Colon = Colon
        self.Comm = Comm
        super().__init__(**kwargs)


class Comment(GoAST):
    """Comments A Comment node represents a single //-style or /*-style comment."""
    _fields = ("Text",)
    """position of '/' starting the comment"""
    Slash: int
    """comment text (excluding '⧵n' for //-style comments)"""
    Text: str

    def __init__(self,
                 Slash: int = 0,
                 Text: str = None,
                 **kwargs) -> None:
        self.Slash = Slash
        self.Text = Text
        super().__init__(**kwargs)


class CommentGroup(GoAST):
    """A CommentGroup represents a sequence of comments with no other tokens and no empty lines
    between.

    line comments; or nil

    associated documentation; or nil
    """
    _fields = ("List",)
    """len(List) > 0"""
    List: List[Comment]

    def __init__(self,
                 List: List[Comment] = None,
                 **kwargs) -> None:
        self.List = List or []
        super().__init__(**kwargs)

def elt_type_from_elts(elts, is_type=False):
    type_func = lambda elt: elt if is_type else elt._type()
    ctx_elts = [x for x in elts if isinstance(x, Ident)]
    e_types = [type_func(elt) for elt in elts if type_func(elt)] or [InterfaceType(_py_context={"elts": ctx_elts})]
    if len(e_types) == 1:
        e_type = e_types[0]
    else:
        for e_type_1, e_type_2 in zip(e_types[:-1], e_types[1:]):
            if e_type_1 != e_type_2:
                e_type = InterfaceType(_py_context={"elts": ctx_elts})
                break
        else:
            e_type = e_types[0]
    return e_type

class CompositeLit(Expr):
    """A CompositeLit node represents a composite literal."""
    _fields = ("Elts", "Incomplete", "Type")
    """list of composite elements; or nil"""
    Elts: List[Expr]
    """true if (source) expressions are missing in the Elts list"""
    Incomplete: bool
    """position of '{'"""
    Lbrace: int
    """position of '}'"""
    Rbrace: int
    """literal type; or nil"""
    Type: Expr

    def __init__(self,
                 Elts: List[Expr] = None,
                 Incomplete: bool = False,
                 Lbrace: int = 0,
                 Rbrace: int = 0,
                 Type: Expr = None,
                 **kwargs) -> None:
        self.Elts = Elts or []
        set_list_type(self.Elts, 'ast.Expr')
        self.Incomplete = Incomplete
        self.Lbrace = Lbrace
        self.Rbrace = Rbrace
        self.Type = Type or MapType()
        super().__init__(**kwargs)

    @classmethod
    def from_List(cls, node: ast.List, **kwargs):
        elts = build_expr_list(node.elts)
        e_type = elt_type_from_elts(elts)
        typ = ArrayType(Elt=e_type)
        return cls(elts, False, 0, 0, typ, **kwargs)

    @classmethod
    def from_Tuple(cls, node: ast.Tuple, **kwargs):
        elts = build_expr_list(node.elts)
        e_type = elt_type_from_elts(elts)
        typ = ArrayType(Elt=e_type, Len=BasicLit.from_int(len(elts)))
        return cls(elts, False, 0, 0, typ, **kwargs)

    @classmethod
    def from_Dict(cls, node: ast.Dict, **kwargs):
        key_elts = build_expr_list(node.keys)
        value_elts = build_expr_list(node.values)
        elts = [KeyValueExpr(Key=key, Value=value) for key, value in zip(key_elts, value_elts)]
        return cls(elts, **kwargs)

    @classmethod
    def from_Set(cls, node: ast.Set, **kwargs):
        key_elts = build_expr_list(node.elts)
        value_elts = [CompositeLit(Type=StructType()) for _ in key_elts]
        elts = [KeyValueExpr(Key=key, Value=value) for key, value in zip(key_elts, value_elts)]
        return cls(elts, Type=MapType(Value=StructType()), **kwargs)

    def _type(self, scope: Optional['Scope']=None, **kwargs):
        if scope:
            match self.Type:
                case ArrayType(Elt=x):
                    x_type = scope._get_type(x, **kwargs)
                    if x_type:
                        return ArrayType(Elt=x_type)
        match self.Type:
            case MapType(Key=key_type, Value=value_type):
                if isinstance(key_type, InterfaceType):
                    key_elts = key_type._py_context.setdefault("elts", [])
                    key_elts += [x.Key for x in self.Elts]
                if isinstance(value_type, InterfaceType):
                    value_elts = value_type._py_context.setdefault("elts", [])
                    value_elts += [x.Value for x in self.Elts]
        return self.Type or super()._type(scope, **kwargs)

class DeclStmt(Stmt):
    """A DeclStmt node represents a declaration in a statement list."""
    _fields = ("Decl",)
    """*GenDecl with CONST, TYPE, or VAR token"""
    Decl: Decl

    def __init__(self,
                 Decl: Decl = None,
                 **kwargs) -> None:
        self.Decl = Decl
        super().__init__(**kwargs)

    @classmethod
    def from_AnnAssign(cls, node: ast.AnnAssign, **kwargs):
        return cls(Decl=build_decl_list([node])[0], **kwargs)


class DeferStmt(Stmt):
    """A DeferStmt node represents a defer statement."""
    _fields = ("Call",)
    Call: CallExpr
    """position of 'defer' keyword"""
    Defer: int

    def __init__(self,
                 Call: CallExpr = None,
                 Defer: int = 0,
                 **kwargs) -> None:
        self.Call = Call
        self.Defer = Defer
        super().__init__(**kwargs)


class Ellipsis(Expr):
    """An Ellipsis node stands for the '...' type in a parameter list or the '...' length in an
    array type.
    """
    _fields = ("Ellipsis", "Elt")
    """position of '...'"""
    Ellipsis: int
    """ellipsis element type (parameter lists only); or nil"""
    Elt: Expr

    def __init__(self,
                 Ellipsis: int = None,
                 Elt: Expr = None,
                 **kwargs) -> None:
        self.Ellipsis = Ellipsis
        self.Elt = Elt
        super().__init__(**kwargs)


class EmptyStmt(Stmt):
    """An EmptyStmt node represents an empty statement. The 'position' of the empty statement is
    the position of the immediately following (explicit or implicit) semicolon.
    """
    _fields = ("Implicit", "Semicolon")
    """if set, ';' was omitted in the source"""
    Implicit: bool
    """position of following ';'"""
    Semicolon: int

    def __init__(self,
                 Implicit: bool = False,
                 Semicolon: int = 0,
                 **kwargs) -> None:
        self.Implicit = Implicit
        self.Semicolon = Semicolon
        super().__init__(**kwargs)

    @classmethod
    def from_Expr(cls, node: ast.Expr):
        match node.value:
            case ast.Constant(value=x) if type(x) == type(...):
                return EmptyStmt()
        raise NotImplementedError(node, node.value)

    @classmethod
    def from_Pass(cls, node: ast.Pass):
        return EmptyStmt()

class ExprStmt(Stmt):
    """An ExprStmt node represents a (stand-alone) expression in a statement list."""
    _fields = ("X",)
    """expression"""
    X: Expr

    def __init__(self,
                 X: Expr = None,
                 **kwargs) -> None:
        self.X = X
        super().__init__(**kwargs)

    @classmethod
    def from_Expr(cls, node: ast.Expr):
        match node.value:
            case ast.Constant(value=Ellipsis()) | ast.Yield() | ast.YieldFrom():
                raise NotImplementedError(node, node.value)

        # We may occasionally decide to bubble up multiple statements in favor of one
        exprs = build_expr_list([node.value])
        results = []
        for expr in exprs:
            # In some rare cases, we may want to bubble up a stmt from build_expr_list to return instead
            if isinstance(expr, Stmt):
                results.append(expr)
            else:
                results.append(cls(expr))
        if len(results) == 1:
            return results[0]
        return results

    @classmethod
    def from_Delete(cls, node: ast.Delete):
        return cls(build_expr_list([node])[0])

    @classmethod
    def from_Raise(cls, node: ast.Raise):
        panic = Ident.from_str("panic")
        exception = node.exc
        panic_msg = _construct_error(exception)
        return cls(X=panic.call(panic_msg))

    @classmethod
    def from_With(cls, node: ast.With):
        body = []
        for with_item in node.items:
            body += build_stmt_list([with_item])
            # TODO: What if there is no optional vars?
            match with_item:
                case ast.withitem(optional_vars=ast.Name()):
                    body.append(DeferStmt(Call=ast_snippets.wrap_err(CallExpr(Args=[], Fun=SelectorExpr(Sel=Ident.from_str("Close"), X=Ident.from_Name(with_item.optional_vars))))))
        body += build_stmt_list(node.body)
        return cls(
            X=CallExpr(
                Args=[],
                Fun=FuncLit(
                    Body=BlockStmt(
                        List=body
                    )
                )
            )
        )

    @classmethod
    def from_Try(cls, node: ast.Try, **kwargs):
        finalbody = []
        if node.finalbody:
            finalbody.append(
                DeferStmt(Call=CallExpr(Fun=FuncLit(Body=BlockStmt(List=build_stmt_list(node.finalbody)))))
            )
        handlerbody = []
        if node.handlers:
            conditional_handlers = []
            conditional_handler_names = []
            base_handler = None
            base_handler_name = None
            for handler in node.handlers:
                is_base_handler = False
                match handler.type:
                    case ast.Tuple(elts=x):
                        cond = ast_snippets.handler_name_to_cond(x[0].id)
                        for subhandler in x[1:]:
                            cond = cond.or_(ast_snippets.handler_name_to_cond(subhandler.id))
                    case None | ast.Name(id="Exception") | ast.Name(id="BaseException"):
                        is_base_handler = True
                    case _:
                        cond = ast_snippets.handler_name_to_cond(handler.type.id)
                if is_base_handler and not base_handler:
                    base_handler = build_stmt_list(handler.body)
                    base_handler_name = None if not handler.name else from_this(Ident, handler.name)
                else:
                    conditional_handlers.append((cond, build_stmt_list(handler.body)))
                    conditional_handler_names.append(None if not handler.name else from_this(Ident, handler.name))
            handlerbody.append(ast_snippets.exceptions(
                conditional_handlers, base_handler, conditional_handler_names, base_handler_name))

        body = finalbody + handlerbody + build_stmt_list(node.body)
        return cls(X=CallExpr(
            Fun=FuncLit(Body=BlockStmt(List=body)),
        **kwargs))


class Field(GoAST):
    """Expressions and types A Field represents a Field declaration list in a struct type, a
    method list in an interface type, or a parameter/result declaration in a signature.
    Field.Names is nil for unnamed parameters (parameter lists which only contain types) and
    embedded struct fields. In the latter case, the field name is the type name.
    """
    _fields = ("Comment", "Doc", "Names", "Tag", "Type")
    """line comments; or nil"""
    Comment: CommentGroup
    """associated documentation; or nil"""
    Doc: CommentGroup
    """field/method/parameter names; or nil"""
    Names: List[Ident]
    """field tag; or nil"""
    Tag: BasicLit
    """field/method/parameter type"""
    Type: Expr

    def __init__(self,
                 Comment: CommentGroup = None,
                 Doc: CommentGroup = None,
                 Names: List[Ident] = None,
                 Tag: BasicLit = None,
                 Type: Expr = None,
                 **kwargs) -> None:
        self.Comment = Comment
        self.Doc = Doc
        self.Names = Names or []
        set_list_type(self.Names, '*ast.Ident')
        self.Tag = Tag
        self.Type = Type or InterfaceType()
        super().__init__(**kwargs)

    @classmethod
    def from_arg(cls, node: ast.arg):
        return cls(None, None, [from_this(Ident, node.arg)], None, _type_annotation_to_go_type(node.annotation)
        if node.annotation else InterfaceType())

    @classmethod
    def from_arguments(cls, node: ast.arguments):
        args = [from_this(cls, arg) for arg in node.args]
        if len(args) == 1:
            return args[0]  # TODO: Deal with defaults?
        return args


    # @classmethod
    # def from_Starred(cls, node: ast.Starred):
    #     print()

    @classmethod
    def from_Name(cls, node: ast.Name, **kwargs):
        return cls(None, None, [], None, from_this(Ident, node), **kwargs)

    @classmethod
    def from_Subscript(cls, node: ast.Subscript, **kwargs):
        return cls(Type=_type_annotation_to_go_type(node), **kwargs)

    @classmethod
    def from_GoBasicType(cls, node: GoBasicType, **kwargs):
        return cls(Type=from_this(Ident, node.value), **kwargs)

    def _type(self):  # TODO: Delete?
        return self.Type or super()._type()


class FieldList(Expr):
    """A FieldList represents a list of Fields, enclosed by parentheses or braces.

    receiver (methods); or nil (functions)

    (incoming) parameters; non-nil

    (outgoing) results; or nil

    list of methods

    list of field declarations
    """
    _fields = ("List",)
    """position of closing parenthesis/brace, if any"""
    Closing: int
    """field list; or nil"""
    List: List[Field]
    """position of opening parenthesis/brace, if any"""
    Opening: int

    def __init__(self,
                 Closing: int = 0,
                 List: List[Field] = None,
                 Opening: int = 0,
                 **kwargs) -> None:
        self.Closing = Closing
        self.List = List or []
        set_list_type(self.List, "*ast.Field")
        self.Opening = Opening
        super().__init__(**kwargs)

    @classmethod
    def from_arguments(cls, node: ast.arguments):
        fields = []
        for arg in [*node.posonlyargs, *node.args, *node.kwonlyargs]:
            fields.append(from_this(Field, arg))
        return cls(List=fields,
                   _py_context={
                       "defaults": build_expr_list(node.defaults),
                       "kw_defaults":build_expr_list(node.kw_defaults),
                       "kwonlyargs": [from_this(Field, p) for p in node.kwonlyargs],
                       "posonlyargs": [from_this(Field, p) for p in node.posonlyargs]
                   })

    @classmethod
    def from_Name(cls, node: ast.Name):
        return cls(List=[from_this(Field, node)])

    @classmethod
    def from_Subscript(cls, node: ast.Subscript, **kwargs):
        return cls(List=[from_this(Field, node)], **kwargs)


class ImportSpec(GoAST):
    """An ImportSpec node represents a single package import."""
    _fields = ("Comment", "Doc", "Name", "Path")
    """line comments; or nil"""
    Comment: CommentGroup
    """associated documentation; or nil"""
    Doc: CommentGroup
    """end of spec (overrides Path.Pos if nonzero)"""
    EndPos: int
    """local package name (including '.'); or nil"""
    Name: Ident
    """import path"""
    Path: BasicLit

    def __init__(self,
                 Comment: CommentGroup = None,
                 Doc: CommentGroup = None,
                 EndPos: int = 0,
                 Name: Ident = None,
                 Path: BasicLit = None,
                 **kwargs) -> None:
        self.Comment = Comment
        self.Doc = Doc
        self.EndPos = EndPos
        self.Name = Name
        self.Path = Path
        super().__init__(**kwargs)


class Scope(GoAST):
    """package scope (this file only)

    package scope across all files

    This file implements scopes and the objects they contain. A Scope maintains the set
    of named language entities declared in the scope and a link to the immediately surrounding
    (outer) scope.
    """
    _fields = ("Objects", "Outer")
    Objects: Dict[str, Object]
    Outer: 'Scope'

    def __init__(self,
                 Objects: Dict[str, Object] = None,
                 Outer: 'Scope' = None,
                 _global: 'Scope' = None,
                 **kwargs) -> None:
        self.Objects = Objects or {}
        self.Outer = Outer
        self._global = Outer._global if Outer else self
        super().__init__(**kwargs)

    def _contains_scope(self, scope: 'Scope') -> bool:
        if self is scope:
            return True
        if self.Outer:
            return self.Outer._contains_scope(scope)
        return False

    def _in_scope(self, obj: Object) -> bool:
        return obj.Name in self.Objects

    def _in_outer_scope(self, obj: Object) -> bool:
        if not self.Outer:
            return False
        return obj.Name in self.Outer.Objects or self.Outer._in_outer_scope(obj)

    def _get_type(self, x, force_current=False, **kwargs):
        scope_checker = self._from_scope if force_current else self._from_scope_or_outer
        match x:
            case Ident():
              obj_name = x.Name
            case str():
              obj_name = x
            case Expr():
                return x._type(scope=self, **kwargs)
            case _:
                warnings.warn(f"Failed to get type for {x}")  # TODO
                return None
        if obj_name in ['true', 'false']:
            return GoBasicType.BOOL.ident
        if obj := scope_checker(obj_name):
            return obj.Type
        if kwargs.get("interface_ok"):
            return InterfaceType(_py_context={"elts": [obj_name]})

    def _get_ctx(self, x):
        match x:
            case Ident():
              obj_name = x.Name
            case str():
              obj_name = x
            case Expr():
                return x._type()
            case _:
                raise ValueError(x)
        if obj := self._from_scope_or_outer(obj_name):
            return obj._py_context

    def _from_scope_or_outer(self, obj_name: str):
        return self._from_scope(obj_name) or self._from_outer_scope(obj_name)

    def _from_scope(self, obj_name: str):
        return self.Objects.get(obj_name)

    def _from_outer_scope(self, obj_name: str):
        if not self.Outer:
            return None
        return self.Outer.Objects.get(obj_name) or self.Outer._from_outer_scope(obj_name)

    def Insert(self, obj: Object) -> Optional[Object]:
        """
        Insert attempts to insert a named object obj into the scope s.
        If the scope already index an object alt with the same name,
        Insert leaves the scope unchanged and returns alt. Otherwise
        it inserts obj and returns nil.
        """
        alt = self.Objects.get(obj.Name)
        if alt:
            return alt
        self.Objects[obj.Name] = obj


class File(GoAST):
    """Files and packages A File node represents a Go source file. The Comments list index
    all comments in the source file in order of appearance, including the comments that are
    pointed to from other nodes via Doc and Comment fields.  For correct printing of source
    code containing comments (using packages go/format and go/printer), special care must be
    taken to update comments when a File's syntax tree is modified: For printing, comments
    are interspersed between tokens based on their position. If syntax tree nodes are removed
    or moved, relevant comments in their vicinity must also be removed (from the
    File.Comments list) or moved accordingly (by updating their positions). A CommentMap may
    be used to facilitate some of these operations.  Whether and how a comment is associated
    with a node depends on the interpretation of the syntax tree by the manipulating program:
    Except for Doc and Comment comments directly associated with nodes, the remaining
    comments are 'free-floating' (see also issues #18593, #20744).
    """
    _fields = ("Comments", "Decls", "Doc", "Imports", "Name", "Package", "Scope", "Unresolved")
    """list of all comments in the source file"""
    Comments: List[CommentGroup]
    """top-level declarations; or nil"""
    Decls: List[Expr]
    """associated documentation; or nil"""
    Doc: CommentGroup
    """imports in this file"""
    Imports: List[ImportSpec]
    """package name"""
    Name: Ident
    """position of 'package' keyword"""
    Package: int
    """package scope (this file only)"""
    Scope: Scope
    """unresolved identifiers in this file"""
    Unresolved: List[Ident]

    def __init__(self,
                 Comments: List[CommentGroup] = None,
                 Decls: List[Expr] = None,
                 Doc: CommentGroup = None,
                 Imports: List[ImportSpec] = None,
                 Name: Ident = None,
                 Package: int = 1,
                 Scope: Scope = None,
                 Unresolved: List[Ident] = None,
                 **kwargs) -> None:
        self.Comments = Comments or []
        set_list_type(self.Comments, "ast.CommentGroup")
        self.Decls = Decls or []
        set_list_type(self.Decls, "ast.Decl")
        self.Doc = Doc
        self.Imports = Imports or []
        set_list_type(self.Imports, "*ast.ImportSpec")
        self.Name = Name
        self.Package = Package
        self.Scope = Scope
        self.Unresolved = Unresolved or []
        set_list_type(self.Unresolved, "ast.Ident")
        super().__init__(**kwargs)

    @classmethod
    def from_Module(cls, node: ast.Module, **kwargs):
        decls = build_decl_list(node.body)
        return cls([], decls, None, [], Ident("main"), 1, None, [], **kwargs)

    def add_import(self, node: ImportSpec):
        self.Imports.append(node)
        self.Decls.insert(0, GenDecl.from_ImportSpec(node))


class ForStmt(Stmt):
    _fields = ("Body", "Cond", "Init", "Post")
    """A ForStmt represents a for statement."""
    Body: BlockStmt
    """finder; or nil"""
    Cond: Expr
    """position of 'for' keyword"""
    For: int
    """initialization statement; or nil"""
    Init: Expr
    """post iteration statement; or nil"""
    Post: Expr

    def __init__(self,
                 Body: BlockStmt = None,
                 Cond: Expr = None,
                 For: int = 0,
                 Init: Expr = None,
                 Post: Expr = None,
                 **kwargs) -> None:
        self.Body = Body
        self.Cond = Cond
        self.For = For
        self.Init = Init
        self.Post = Post
        super().__init__(**kwargs)

    @classmethod
    def from_While(cls, node: ast.While):
        body = from_this(BlockStmt, node.body)
        cond = build_expr_list([node.test])[0]
        match cond:
            case Ident(Name="true"):
                return cls(Body=body)
            case BasicLit(Value=x) if not json.loads(x):
                return cls(Body=body, Cond=Ident.from_str("false"))
            case BasicLit(Kind=x) if x in [token.INT, token.STRING, token.FLOAT]:
                return cls(Body=body)
            case Ident(Name="false") | Ident(Name="nil"):
                return cls(Body=body, Cond=Ident.from_str("false"))

        return cls(Body=body, Cond=cond)


class FuncType(Expr):
    """function signature: parameters, results, and position of 'func' keyword

    function type

    Pointer types are represented via StarExpr nodes. A FuncType node represents a function
    type.
    """
    _fields = ("Params", "Results")
    """position of 'func' keyword (token.NoPos if there is no 'func')"""
    Func: int
    """(incoming) parameters; non-nil"""
    Params: FieldList
    """(outgoing) results; or nil"""
    Results: FieldList

    def __init__(self,
                 Func: int = 0,
                 Params: FieldList = None,
                 Results: FieldList = None,
                 **kwargs) -> None:
        self.Func = Func
        self.Params = Params
        self.Results = Results
        super().__init__(**kwargs)

    @classmethod
    def from_FunctionDef(cls, node: ast.FunctionDef, **kwargs):
        params = from_this(FieldList, node.args)
        match node.returns:
            case None | ast.Constant(value=None):
                results = None
            case _:
                results = from_this(FieldList, node.returns)
        return cls(0, params, results, **kwargs)

    @classmethod
    def from_AsyncFunctionDef(cls, node: ast.AsyncFunctionDef, **kwargs):
        func_type = cls.from_FunctionDef(node, **kwargs)
        # TODO: Multiple return values should be a struct or something?
        match func_type.Results:
            case FieldList(List=[f]):
                f.Type = ChanType(Value=f.Type, Dir=2)
            case _:
                func_type.Results = FieldList(List=[Field(Type=ChanType())], Dir=2)
        return func_type

    @classmethod
    def from_Lambda(cls, node: ast.Lambda, **kwargs):
        params = from_this(FieldList, node.args)
        t = build_expr_list([node.body])[0]._type()
        return cls(0, params, FieldList(List=[Field(Type=t)]) if t else FieldList(List=[]), **kwargs)


class FuncDecl(Decl):
    """A FuncDecl node represents a function declaration."""
    _fields = ("Body", "Doc", "Name", "Recv", "Type")
    """function body; or nil for external (non-Go) function"""
    Body: BlockStmt
    """associated documentation; or nil"""
    Doc: CommentGroup
    """function/method name"""
    Name: Ident
    """receiver (methods); or nil (functions)"""
    Recv: FieldList
    """function signature: parameters, results, and position of 'func' keyword"""
    Type: FuncType

    def __init__(self,
                 Body: BlockStmt = None,
                 Doc: CommentGroup = None,
                 Name: Ident = None,
                 Recv: FieldList = None,
                 Type: FuncType = None,
                 **kwargs) -> None:
        self.Body = Body
        self.Doc = Doc
        self.Name = Name
        self.Recv = Recv
        self.Type = Type
        super().__init__(**kwargs)

    @classmethod
    def from_FunctionDef(cls, node: ast.FunctionDef, **kwargs):
        body = from_this(BlockStmt, node.body)
        doc = None
        name = from_this(Ident, node.name)
        recv = None
        _type = FuncType.from_FunctionDef(node)
        return cls(body, doc, name, recv, _type, **kwargs)

    @classmethod
    def from_AsyncFunctionDef(cls, node: ast.AsyncFunctionDef, **kwargs):
        if node.name == "main":
            # TODO: There are other situations where we probably want to just disregard
            #   the async aspect of the function definition, likely more easy to interpret
            #   as part of post-processing.
            #   One idea for how I could handle this in post without reversing
            #   all the logic is to store a deepcopy of the functionDef version as part of the
            #   asyncFunctionDef and recover it in an early transformation stage.
            #   For now, though, this will do.
            return cls.from_FunctionDef(node, **kwargs)
        r = Ident("r")
        _type = FuncType.from_AsyncFunctionDef(node)
        body = from_this(BlockStmt, node.body)
        # TODO: Multi-return?
        _replace_nodes(
            body,
            replacer=lambda x: SendStmt(Chan=r, Value=x.Results[0]) if isinstance(x, ReturnStmt) else x,
            skipper=lambda x: isinstance(x, FuncLit)
        )
        body.List.insert(0, DeferStmt(Call=Ident("close").call(r)))
        make_chan_type = ChanType(Value=_type.Results.List[0].Type.Value, Dir=3)
        body = BlockStmt(List=[
            r.assign(Ident("make").call(make_chan_type)),
            GoStmt(Call=FuncLit(Body=body).call()),
            r.return_()
        ])
        doc = None
        name = from_this(Ident, node.name)
        recv = None
        return cls(body, doc, name, recv, _type, **kwargs)

    @classmethod
    def from_global_code(cls, node: ast.AST, **kwargs):
        body = from_this(BlockStmt, [node])
        doc = None
        name = from_this(Ident, "init")
        recv = None
        _type = FuncType(0, FieldList(0, []), FieldList(0, []))
        return cls(body, doc, name, recv, _type, **kwargs)


class FuncLit(Expr):
    """A FuncLit node represents a function literal."""
    _fields = ("Body", "Type")
    """function body"""
    Body: BlockStmt
    """function type"""
    Type: FuncType

    CONVERSION_ORDER = {
        ast.Lambda: -1,
        ast.FunctionDef: -1
    }

    def __init__(self,
                 Body: BlockStmt = None,
                 Type: FuncType = None,
                 **kwargs) -> None:
        self.Body = Body
        self.Type = Type or FuncType()
        super().__init__(**kwargs)

    @classmethod
    def from_FunctionDef(cls, node: ast.FunctionDef, **kwargs):
        body = from_this(BlockStmt, node.body)
        _type = from_this(FuncType, node)
        return cls(body, _type, **kwargs)

    @classmethod
    def from_Lambda(cls, node: ast.Lambda, **kwargs):
        body = BlockStmt(List=[ReturnStmt(build_expr_list([node.body]))])
        _type = from_this(FuncType, node)
        return cls(body, _type, **kwargs)

    def _type(self, scope: Optional['Scope']=None, interface_ok=False, **kwargs):
        return self.Type or super()._type(scope, interface_ok, **kwargs)

class GenDecl(Decl):
    """A GenDecl node (generic declaration node) represents an import, constant, type or
    variable declaration. A valid Lparen position (Lparen.IsValid()) indicates a
    parenthesized declaration.  Relationship between Tok value and Specs element type:
    token.IMPORT  *ImportSpec token.CONST   *ValueSpec token.TYPE    *TypeSpec token.VAR
    *ValueSpec
    """
    _fields = ("Doc", "Specs", "Tok")
    """associated documentation; or nil"""
    Doc: CommentGroup
    """position of '(', if any"""
    Lparen: int
    """position of ')', if any"""
    Rparen: int
    Specs: List[Expr]
    """IMPORT, CONST, TYPE, VAR"""
    Tok: token
    """position of Tok"""
    TokPos: int

    def __init__(self,
                 Doc: CommentGroup = None,
                 Lparen: int = 0,
                 Rparen: int = 0,
                 Specs: List[Expr] = None,
                 Tok: token = 0,
                 TokPos: int = 0,
                 **kwargs) -> None:
        self.Doc = Doc
        self.Lparen = Lparen
        self.Rparen = Rparen
        self.Specs = Specs or []
        set_list_type(self.Specs, "ast.Spec")
        self.Tok = Tok
        self.TokPos = TokPos
        super().__init__(**kwargs)

    @classmethod
    def from_Import(cls, node: ast.Import, **kwargs):

        return cls(Specs=[ImportSpec(None, None, 0, from_this(Ident, x.asname) if x.asname else None,
                                           BasicLit(token.STRING, x.name, 0)) for x in node.names],
                   Tok=token.IMPORT, **kwargs)

    @classmethod
    def from_ClassDef(cls, node: ast.ClassDef, **kwargs):
        # Returns a list of declarations
        fields_dict = {}
        methods = []
        for obj in node.body:
            match obj:
                case ast.AnnAssign():
                    assignment = build_stmt_list([obj])[0]
                    for spec in assignment.Decl.Specs:
                        for name in spec.Names:
                            if name.Name in fields_dict:
                                if fields_dict[name.Name].Type == InterfaceType() and spec.Type:
                                    fields_dict[name.Name].Type = spec.Type
                            else:
                                fields_dict[name.Name] = Field(Type=spec.Type, Names=[name])
                case ast.Assign():
                    ... # TODO
                case ast.FunctionDef():
                    methods.append(obj)
                    func_def = build_stmt_list([obj])[0]
                    f = func_def.Rhs[0]
                    try:
                        self_name = f.Params.List[0].Names[0].Name
                    except IndexError:  # staticmethod
                        self_name = "static"
                    except AttributeError:  # Function literal
                        self_name = ""
                    def _matcher(_node: 'ast.AST'):
                        match _node:
                            case AssignStmt(Lhs=[SelectorExpr(X=Ident(Name=x))]):
                                if self_name == x:
                                    return _node
                    assignment_exprs = _find_nodes(f, _matcher)
                    for assignment in assignment_exprs:
                        match assignment:
                            case AssignStmt(Lhs=[SelectorExpr(Sel=name)], Rhs=[expr]):
                                _type = expr._type()
                                if name.Name in fields_dict:
                                    if fields_dict[name.Name].Type == InterfaceType() and _type:
                                        fields_dict[name.Name].Type = _type
                                else:
                                    fields_dict[name.Name] = Field(Type=_type, Names=[name])
                case _:
                    # Real assignments in the body not yet supported...
                    raise NotImplementedError(node, obj)
        fields = list(fields_dict.values())
        self_ident = Ident.from_str(node.name)
        specs = [TypeSpec(Name=self_ident, Type=StructType(FieldList(List=fields)))]
        decls = [cls(Tok=token.TYPE, Specs=specs, **kwargs)]
        method_decls = build_decl_list(methods)
        for method in method_decls:
            try:
                recv = FieldList(List=[method.Type.Params.List[0]])
                recv.List[0].Type = StarExpr(X=self_ident)
                del method.Type.Params.List[0]
                match method.Name.Name:
                    case '__init__':
                        method.Body.List.insert(0, AssignStmt(Lhs=list(recv.List[0].Names),
                                                              Rhs=[Ident.from_str("new").call(self_ident)]))
                        method.Body.List.append(ReturnStmt())
                        method.Name = Ident.from_str(f"New{node.name}")
                        method.Type.Results = recv
                    case _:
                        method.Recv = recv
            except IndexError:
                pass  # TODO: determine ramifications of ignoring this case
        decls += method_decls
        return decls

    @classmethod
    def from_Assign(cls, node: ast.Assign, global_mode=False, **kwargs):
        values = build_expr_list([node.value])
        spec = ValueSpec(Values=values, Names=build_expr_list(node.targets))
        if global_mode:
            # If we've already initialized some code via init methods,
            #   to get close to the behavior of python we need to initialize
            #   all subsequent vars via init as well
            _type = None
            _desperate_type = None
            values = values.copy()
            while spec.Values:
                value = spec.Values.pop(0)
                _type = _type or value._type()
                if not _type:
                    _desperate_type = _desperate_type or value._type(interface_ok=True)
            spec.Type = _type or InterfaceType(_py_context={"elts": values})
            init = FuncDecl.from_global_code(node)
            init.Body.List[0].Tok = token.ASSIGN
            return [init, cls(Tok=token.VAR, Specs=[spec], **kwargs)]
        return cls(Tok=token.VAR, Specs=[spec], **kwargs)

    @classmethod
    def from_AnnAssign(cls, node: ast.AnnAssign, global_mode=False, **kwargs):
        values = build_expr_list([node.value]) if node.value else None
        spec = ValueSpec(Values=values, Type=_type_annotation_to_go_type(node.annotation),
                           Names=[from_this(Ident, node.target)])
        if values and global_mode:
            init = FuncDecl.from_global_code(ast.Assign(targets=[node.target], value=node.value))
            init.Body.List[0].Tok = token.ASSIGN
            spec.Values = []
            return [init, cls(Tok=token.VAR, Specs=[spec], **kwargs)]
        return cls(Tok=token.VAR, Specs=[spec], **kwargs)

    @classmethod
    def from_ImportSpec(cls, node: ImportSpec, **kwargs):
        return cls(Specs=[node], Tok=token.IMPORT, **kwargs)

    @classmethod
    def from_ImportFrom(cls, node: ast.ImportFrom, **kwargs):
        specs = []
        for x in node.names:
            name = "." if x.name == "*" else x.asname
            name = from_this(Ident, name) if name else None
            if x.name == "*":
                path_str = '/'.join([node.module, x.name])
            else:
                path_str = node.module
            specs.append(ImportSpec(None, None, 0, name, Path=BasicLit(token.STRING, path_str, 0)))
        return cls(None, 0, 0, specs, token.IMPORT, 0, **kwargs)


class GoStmt(Stmt):
    """A GoStmt node represents a go statement."""
    _fields = ("Call",)
    Call: CallExpr
    """position of 'go' keyword"""
    Go: int

    def __init__(self,
                 Call: CallExpr = None,
                 Go: int = 0,
                 **kwargs) -> None:
        self.Call = Call
        self.Go = Go
        super().__init__(**kwargs)


class IfStmt(Stmt):
    """An IfStmt node represents an if statement."""
    _fields = ("Body", "Cond", "Else", "Init")
    Body: BlockStmt
    """finder"""
    Cond: Expr
    """else branch; or nil"""
    Else: Stmt
    """position of 'if' keyword"""
    If: int
    """initialization statement; or nil"""
    Init: Stmt

    def __init__(self,
                 Body: BlockStmt = None,
                 Cond: Expr = None,
                 Else: Stmt = None,
                 If: int = 0,
                 Init: Stmt = None,
                 **kwargs) -> None:
        self.Body = Body
        self.Cond = Cond
        self.Else = Else
        self.If = If
        self.Init = Init
        super().__init__(**kwargs)

    @classmethod
    def from_If(cls, node: ast.If, **kwargs):
        body = from_this(BlockStmt, node.body)
        cond = build_expr_list([node.test])[0]
        _else = build_stmt_list(node.orelse)
        if len(_else) == 0:
            _else = None
        elif len(_else) == 1:
            _else = _else[0]
        else:
            _else = BlockStmt(List=_else)
        return cls(body, cond, _else, **kwargs)

    @classmethod
    def from_Assert(cls, node: ast.Assert, **kwargs):
        panic = Ident.from_str("panic")
        body = BlockStmt(List=[ExprStmt(X=panic.call(_construct_error(node)))])
        cond = UnaryExpr(X=build_expr_list([node.test])[0], Op=token.NOT)
        return cls(body, cond, **kwargs)

    @classmethod
    def from_IfExp(cls, node: ast.IfExp, action: Optional[Callable[['Expr'], 'Stmt']]=None, **kwargs):
        if action is None:
            action = lambda x: ExprStmt(X=x)

        body = BlockStmt(List=[action(build_expr_list([node.body])[0])])
        cond = build_expr_list([node.test])[0]
        if node.orelse:
            _else = BlockStmt(List=[action(build_expr_list([node.orelse])[0])])
        else:
            _else = None
        return cls(body, cond, _else, **kwargs)

class IncDecStmt(Stmt):
    """An IncDecStmt node represents an increment or decrement statement."""
    _fields = ("Tok", "X")
    """INC or DEC"""
    Tok: token
    """position of Tok"""
    TokPos: int
    X: Expr

    def __init__(self,
                 Tok: token = None,
                 TokPos: int = 0,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Tok = Tok
        self.TokPos = TokPos
        self.X = X
        super().__init__(**kwargs)


class IndexExpr(Expr):
    """An IndexExpr node represents an expression followed by an index."""
    _fields = ("Index", "X")
    """index expression"""
    Index: Expr
    """position of '['"""
    Lbrack: int
    """position of ']'"""
    Rbrack: int
    """expression"""
    X: Expr

    def __init__(self,
                 Index: Expr = None,
                 Lbrack: int = 0,
                 Rbrack: int = 0,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Index = Index
        self.Lbrack = Lbrack
        self.Rbrack = Rbrack
        self.X = X
        super().__init__(**kwargs)

    @classmethod
    def from_Subscript(cls, node: ast.Subscript, **kwargs):
        match node.slice:
            case ast.Constant() | ast.UnaryOp() | ast.Name() | ast.Call() | ast.BinOp() | ast.Tuple():
                index = build_expr_list([node.slice])[0]
            case _:
                raise NotImplementedError((node, node.slice))
        x = build_expr_list([node.value])[0]
        return cls(index, X=x, **kwargs)

    def _type(self, scope: Optional['Scope']=None, **kwargs):
        if scope:
            x_type = scope._get_type(self.X, **kwargs)
            index_type = scope._get_type(self.Index, **kwargs)
        else:
            x_type = self.X._type(scope, **kwargs)
            index_type = self.Index._type(scope, **kwargs)
        # If we're taking a slice, the type doesn't change
        t = None

        # TODO: Check if we're forgetting any composite types
        if index_type == GoBasicType.INT.ident and isinstance(x_type, ArrayType):
            t = x_type.Elt
        elif isinstance(x_type, MapType):
            return x_type.Value
        elif index_type and (index_type != GoBasicType.INT.ident) and not isinstance(index_type, InterfaceType):
            t = x_type

        # If X is a string and we're indexing it, it's a byte
        if x_type == GoBasicType.STRING.ident:
            t = t or GoBasicType.BYTE.ident

        return t or super()._type(scope, **kwargs)


class InterfaceType(Expr):
    """An InterfaceType node represents an interface type."""
    _fields = ("Incomplete", "Methods")
    """true if (source) methods are missing in the Methods list"""
    Incomplete: bool
    """position of 'interface' keyword"""
    Interface: int
    """list of methods"""
    Methods: FieldList

    def __init__(self,
                 Incomplete: bool=False,
                 Interface: int=0,
                 Methods: FieldList=None,
                 **kwargs) -> None:
        self.Incomplete = Incomplete
        self.Interface = Interface
        self.Methods = Methods or FieldList()
        super().__init__(**kwargs)


class KeyValueExpr(Expr):
    """A KeyValueExpr node represents (key : value) pairs in composite literals."""
    _fields = ("Key", "Value")
    """position of ':'"""
    Colon: int
    Key: Expr
    Value: Expr

    def __init__(self,
                 Colon: int = 0,
                 Key: Expr = None,
                 Value: Expr = None,
                 **kwargs) -> None:
        self.Colon = Colon
        self.Key = Key
        self.Value = Value
        super().__init__(**kwargs)


class LabeledStmt(Stmt):
    """A LabeledStmt node represents a labeled statement."""
    _fields = ("Label", "Stmt")
    """position of ':'"""
    Colon: int
    Label: Ident
    Stmt: Stmt

    def __init__(self,
                 Colon: int = 0,
                 Label: Ident = None,
                 Stmt: Stmt = None,
                 **kwargs) -> None:
        self.Colon = Colon
        self.Label = Label
        self.Stmt = Stmt
        super().__init__(**kwargs)


class MapType(Expr):
    """A MapType node represents a map type."""
    _fields = ("Key", "Value")
    Key: Expr
    """position of 'map' keyword"""
    Map: int
    Value: Expr

    def __init__(self,
                 Key: Expr = None,
                 Map: int = 0,
                 Value: Expr = None,
                 **kwargs) -> None:
        self.Key = Key or InterfaceType()
        self.Map = Map
        self.Value = Value or InterfaceType()
        super().__init__(**kwargs)


class Package(GoAST):
    """A Package node represents a set of source files collectively building a Go package."""
    _fields = ("Files", "Imports", "Name", "Scope")
    """Go source files by filename"""
    Files: Dict[str, File]
    """map of package id -> package object"""
    Imports: Dict[str, Object]
    """package name"""
    Name: str
    """package scope across all files"""
    Scope: Scope

    def __init__(self,
                 Files: Dict[str, File] = None,
                 Imports: Dict[str, Object] = None,
                 Name: str = None,
                 Scope: Scope = None,
                 **kwargs) -> None:
        self.Files = Files or {}
        self.Imports = Imports or {}
        self.Name = Name
        self.Scope = Scope
        super().__init__(**kwargs)


class ParenExpr(Expr):
    """A ParenExpr node represents a parenthesized expression."""
    _fields = ("X",)
    """position of '('"""
    Lparen: int
    """position of ')'"""
    Rparen: int
    """parenthesized expression"""
    X: Expr

    def __init__(self,
                 Lparen: int = 0,
                 Rparen: int = 0,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Lparen = Lparen
        self.Rparen = Rparen
        self.X = X
        super().__init__(**kwargs)


class RangeStmt(Stmt):
    """A RangeStmt represents a for statement with a range clause."""
    _fields = ("Body", "Key", "Tok", "Value", "X")
    Body: BlockStmt
    """position of 'for' keyword"""
    For: int
    Key: Expr
    """ILLEGAL if Key == nil, ASSIGN, DEFINE"""
    Tok: token
    """position of Tok; invalid if Key == nil"""
    TokPos: int
    Value: Expr
    """value to range over"""
    X: Expr

    def __init__(self,
                 Body: BlockStmt = None,
                 For: int = 0,
                 Key: Expr = None,
                 Tok: token = None,
                 TokPos: int = 0,
                 Value: Expr = None,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Body = Body
        self.For = For
        self.Key = Key
        self.Tok = Tok
        self.TokPos = TokPos
        self.Value = Value
        self.X = X
        super().__init__(**kwargs)

    @classmethod
    def from_For(cls, node: ast.For, **kwargs):
        body = from_this(BlockStmt, node.body)
        tok = token.DEFINE
        key = Ident.from_str("_")
        value = build_expr_list([node.target])[0]
        x = build_expr_list([node.iter])[0]
        return cls(Body=body, Key=key, Tok=tok, Value=value, X=x, **kwargs)

    @classmethod
    def from_comprehension(cls, node: ast.comprehension, **kwargs):
        body = BlockStmt()
        tok = token.DEFINE
        key = Ident.from_str("_")
        value = build_expr_list([node.target])[0]
        ifs = build_expr_list(node.ifs)
        ifs.reverse()
        low = body
        while ifs:
            low.List.append(IfStmt(Body=BlockStmt(), Cond=ifs.pop()))
            low = low.List[0].Body
        x = build_expr_list([node.iter])[0]
        return cls(Body=body, Key=key, Tok=tok, Value=value, X=x, **kwargs)


class ReturnStmt(Stmt):
    """A ReturnStmt node represents a return statement."""
    _fields = ("Results",)
    """result expressions; or nil"""
    Results: List[Expr]
    """position of 'return' keyword"""
    Return: int

    def __init__(self,
                 Results: List[Expr] = None,
                 Return: int = 0,
                 **kwargs) -> None:
        self.Results = Results or []
        set_list_type(self.Results, "ast.Expr")
        self.Return = Return
        super().__init__(**kwargs)

    @classmethod
    def from_Return(cls, node: ast.Return, **kwargs):
        return cls(build_expr_list([node.value]) if node.value else None, **kwargs)


class SelectStmt(Stmt):
    """A SelectStmt node represents a select statement."""
    _fields = ("Body",)
    """CommClauses only"""
    Body: BlockStmt
    """position of 'select' keyword"""
    Select: int

    def __init__(self,
                 Body: BlockStmt = None,
                 Select: int = 0,
                 **kwargs) -> None:
        self.Body = Body
        self.Select = Select
        super().__init__(**kwargs)


class SelectorExpr(Expr):
    """A SelectorExpr node represents an expression followed by a selector."""
    _fields = ("Sel", "X",)
    """field selector"""
    Sel: Ident
    """expression"""
    X: Expr

    def __init__(self,
                 Sel: Ident = None,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Sel = Sel
        self.X = X
        super().__init__(**kwargs)

    @classmethod
    def from_Attribute(cls, node: ast.Attribute, **kwargs):
        attr = build_expr_list([node.attr])[0]
        x = build_expr_list([node.value])[0]
        return cls(Sel=attr, X=x, **kwargs)


class SendStmt(Stmt):
    """A SendStmt node represents a send statement."""
    _fields = ("Chan", "Value")
    """position of '<-'"""
    Arrow: int
    Chan: Expr
    Value: Expr

    def __init__(self,
                 Arrow: int = 0,
                 Chan: Expr = None,
                 Value: Expr = None,
                 **kwargs) -> None:
        self.Arrow = Arrow
        self.Chan = Chan
        self.Value = Value
        super().__init__(**kwargs)

    @classmethod
    def from_Expr(cls, node: ast.Expr, **kwargs):
        match node.value:
            case ast.Yield():
                # Returns an additional UnaryExpr
                return [
                    cls(Chan=Ident("yield"), Value=build_expr_list([node.value.value])[0], **kwargs),
                   Ident("wait").receive().stmt()
                ]
            case _:
                raise NotImplementedError()

class SliceExpr(Expr):
    """A SliceExpr node represents an expression followed by slice indices."""
    _fields = ("High", "Low", "Max", "Slice3", "X",)
    """end of slice range; or nil"""
    High: Expr
    """position of '['"""
    Lbrack: int
    """start of slice range; or nil"""
    Low: Expr
    """maximum capacity of slice; or nil"""
    Max: Expr
    """position of ']'"""
    Rbrack: int
    """true if 3-index slice (2 colons present)"""
    Slice3: bool
    """expression"""
    X: Expr

    def __init__(self,
                 High: Expr = None,
                 Lbrack: int = 0,
                 Low: Expr = None,
                 Max: Expr = None,
                 Rbrack: int = 0,
                 Slice3: bool = None,
                 X: Expr = None,
                 **kwargs) -> None:
        self.High = High
        self.Lbrack = Lbrack
        self.Low = Low
        self.Max = Max
        self.Rbrack = Rbrack
        self.Slice3 = Slice3
        self.X = X
        super().__init__(**kwargs)

    @classmethod
    def from_Subscript(cls, node: ast.Subscript, **kwargs):
        match node.slice:
            case ast.Slice():
                low = build_expr_list([node.slice.lower])[0] if node.slice.lower else None
                high = build_expr_list([node.slice.upper])[0] if node.slice.upper else None
            case _:
                raise NotImplementedError((node, node.slice))
        x = build_expr_list([node.value])[0]
        return cls(High=high, Low=low, X=x, **kwargs)

    def _type(self, scope: Optional[Scope] = None, **kwargs):
        if scope:
            x_type = scope._get_type(self.X, **kwargs)
            if x_type:
                return x_type
        return super()._type(scope, **kwargs)


class StarExpr(Expr):
    """A StarExpr node represents an expression of the form '*' Expression. Semantically it
    could be a unary '*' expression, or a pointer type.
    """
    _fields = ("Star", "X")
    """position of '*'"""
    Star: int
    """operand"""
    X: Expr

    def __init__(self,
                 Star: int = 0,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Star = Star
        self.X = X
        super().__init__(**kwargs)

    @classmethod
    def from_BinOp(cls, node: ast.BinOp, **kwargs):
        """
        '*'@X -> *X
        This isn't a Python thing. It's just a way to explicitly reference starred expressions
        """
        match node:
            case ast.BinOp(left=ast.Constant(value='*')):
                pass
            case _:
                raise ValueError()
        X = build_expr_list([node.right])[0]
        return cls(X=X, **kwargs)

    def _type(self, scope: Optional['Scope'] = None, interface_ok=False, **kwargs):
        x_type = None
        if scope:
            if t := scope._get_type(self.X, interface_ok=interface_ok, **kwargs):
                x_type = t
        else:
            if t := self.X._type(scope, interface_ok, **kwargs):
                x_type = t
        if x_type:
            match x_type:
                case StarExpr():
                    return x_type.X
        return super()._type(scope, interface_ok, **kwargs)


class StructType(Expr):
    """A StructType node represents a struct type."""
    _fields = ("Fields", "Incomplete")
    """list of field declarations"""
    Fields: FieldList
    """true if (source) fields are missing in the Fields list"""
    Incomplete: bool
    """position of 'struct' keyword"""
    Struct: int

    def __init__(self,
                 Fields: FieldList = None,
                 Incomplete: bool = False,
                 Struct: int = 0,
                 *args,
                 **kwargs) -> None:
        self.Fields = Fields or FieldList()
        self.Incomplete = Incomplete
        self.Struct = Struct
        super().__init__(**kwargs)


class SwitchStmt(Stmt):
    """A SwitchStmt node represents an expression switch statement."""
    _fields = ("Body", "Init", "Tag")
    """CaseClauses only"""
    Body: BlockStmt
    """initialization statement; or nil"""
    Init: Stmt
    """position of 'switch' keyword"""
    Switch: int
    """tag expression; or nil"""
    Tag: Expr

    def __init__(self,
                 Body: BlockStmt = None,
                 Init: Stmt = None,
                 Switch: int = 0,
                 Tag: Expr = None,
                 **kwargs) -> None:
        self.Body = Body
        self.Init = Init
        self.Switch = Switch
        self.Tag = Tag
        super().__init__(**kwargs)

    @classmethod
    def from_Match(cls, node: ast.Match, **kwargs):
        tag = build_expr_list([node.subject])[0]
        body = []
        # Avoiding build_expr_list here because we'll probably be passing in more context later
        for case in node.cases:
            body.append(CaseClause.from_match_case(case))
        return cls(Tag=tag, Body=BlockStmt(List=body))


class TypeAssertExpr(Expr):
    """A TypeAssertExpr node represents an expression followed by a type assertion."""
    _fields = ("Type", "X")
    """position of '('"""
    Lparen: int
    """position of ')'"""
    Rparen: int
    """asserted type; nil means type switch X.(type)"""
    Type: Expr
    """expression"""
    X: Expr

    def __init__(self,
                 Lparen: int = 0,
                 Rparen: int = 0,
                 Type: Expr = None,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Lparen = Lparen
        self.Rparen = Rparen
        self.Type = Type
        self.X = X
        super().__init__(**kwargs)


class TypeSpec(GoAST):
    """A TypeSpec node represents a type declaration (TypeSpec production)."""
    _fields = ("Comment", "Doc", "Name", "Type")
    """position of '=', if any"""
    Assign: int
    """line comments; or nil"""
    Comment: CommentGroup
    """associated documentation; or nil"""
    Doc: CommentGroup
    """type name"""
    Name: Ident
    """*Ident, *ParenExpr, *SelectorExpr, *StarExpr, or any of the *XxxTypes"""
    Type: Expr

    def __init__(self,
                 Assign: int = 0,
                 Comment: CommentGroup = None,
                 Doc: CommentGroup = None,
                 Name: Ident = None,
                 Type: Expr = None,
                 **kwargs) -> None:
        self.Assign = Assign
        self.Comment = Comment
        self.Doc = Doc
        self.Name = Name
        self.Type = Type
        super().__init__(**kwargs)


class TypeSwitchStmt(Stmt):
    """A TypeSwitchStmt node represents a type switch statement."""
    _fields = ("Body", "Init", "Assign")
    """x := y.(type) or y.(type)"""
    Assign: Expr
    """CaseClauses only"""
    Body: BlockStmt
    """initialization statement; or nil"""
    Init: Expr
    """position of 'switch' keyword"""
    Switch: int

    CONVERSION_ORDER = {
        ast.If: -1
    }

    def __init__(self,
                 Assign: Expr = None,
                 Body: BlockStmt = None,
                 Init: Expr = None,
                 Switch: int = 0,
                 **kwargs) -> None:
        self.Assign = Assign
        self.Body = Body
        self.Init = Init
        self.Switch = Switch
        super().__init__(**kwargs)

    @classmethod
    def from_If(cls, node: ast.If):
        body = from_this(BlockStmt, node.body)

        match node.test:
            case ast.Call(func=ast.Name(id="isinstance"), args=[__expr, __types]):
                _expr = build_expr_list([__expr])[0]
                try:
                    _types = [_type_annotation_to_go_type(x) for x in __types.elts]
                except AttributeError:
                    _types = [_type_annotation_to_go_type(__types)]
            case _:
                raise NotImplementedError()

        _else = build_stmt_list(node.orelse)
        if len(_else) == 0:
            _else = None

        assign = TypeAssertExpr(X=_expr).stmt()
        cases = [CaseClause(Body=body.List.copy(), List=_types)]


        match _else:
            case None:
                pass
            case [TypeSwitchStmt(Body=BlockStmt(List=nested_cases))]:
                cases += nested_cases
            case [ExprStmt(), *others]:
                cases += [CaseClause(Body=_else)]
            case _:
                raise NotImplementedError(node)

        return cls(Assign=assign, Body=BlockStmt(List=cases))



class UnaryExpr(Expr):
    """A UnaryExpr node represents a unary expression. Unary '*' expressions are represented via
    StarExpr nodes.
    """
    _fields = ("Op", "X")
    """operator"""
    Op: token
    """position of Op"""
    OpPos: int
    """operand"""
    X: Expr

    @classmethod
    def from_UnaryOp(cls,
                     node: ast.UnaryOp = None,
                     **kwargs):
        match node.op:
            case ast.USub(): op = token.SUB
            case ast.UAdd(): op = ast.UAdd
            case ast.Not(): op = token.NOT
            case _: raise NotImplementedError((node, node.op))
        X = build_expr_list([node.operand])[0]
        return cls(Op=op, X=X, **kwargs)

    @classmethod
    def from_Await(cls, node: ast.Await, **kwargs):
        X = build_expr_list([node.value])[0]
        return cls(Op=token.ARROW, X=X, **kwargs)

    def __init__(self,
                 Op: token = None,
                 OpPos: int = 0,
                 X: Expr = None,
                 **kwargs) -> None:
        self.Op = Op
        self.OpPos = OpPos
        self.X = X
        super().__init__(**kwargs)

    def _type(self, scope: Optional['Scope'] = None, **kwargs):
        wrapper = lambda x: StarExpr(X=x) if self.Op == token.AND else x
        if scope:
            t = scope._get_type(self.X, **kwargs) or super()._type(scope, **kwargs)
        else:
            t = self.X._type(scope, **kwargs) or super()._type(scope, **kwargs)
        if t:
            wrapped = wrapper(t)
            return wrapped
        return super()._type(scope, **kwargs)


class ValueSpec(Expr):
    """A ValueSpec node represents a constant or variable declaration (ConstSpec or VarSpec
    production).
    """
    _fields = ("Comment", "Doc", "Names", "Type", "Values")
    """line comments; or nil"""
    Comment: CommentGroup
    """associated documentation; or nil"""
    Doc: CommentGroup
    """value names (len(Names) > 0)"""
    Names: List[Ident]
    """value type; or nil"""
    Type: Expr
    """initial values; or nil"""
    Values: List[Expr]

    def __init__(self,
                 Comment: CommentGroup = None,
                 Doc: CommentGroup = None,
                 Names: List[Ident] = None,
                 Type: Expr = None,
                 Values: List[Expr] = None,
                 **kwargs) -> None:
        self.Comment = Comment
        self.Doc = Doc
        self.Names = Names or []
        set_list_type(self.Names, '*ast.Ident')
        self.Type = Type
        self.Values = Values or []
        set_list_type(self.Values, 'ast.Expr')
        super().__init__(**kwargs)


def _get_subclasses_of(parent_type):
    return [globals()[x] for x in globals() if inspect.isclass(globals()[x]) and issubclass(globals()[x], parent_type)]


_DECL_TYPES = _get_subclasses_of(Decl)
_STMT_TYPES = _get_subclasses_of(Stmt)
_EXPR_TYPES = _get_subclasses_of(Expr)

# Dumping
_LIST_TYPES = {}


def get_list_type(li: list):
    return _LIST_TYPES.get(id(li), 'interface{}')


def set_list_type(li: list, typ: str):
    _LIST_TYPES[id(li)] = typ

# Quality of life
len_ = Ident("len").call