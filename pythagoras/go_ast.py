import os
import uuid
import ast
import json
from enum import Enum
from subprocess import Popen, PIPE
from typing import List, Any, Dict, Union

Expr = Union[List[Any], bool, float, int, Dict[str, Any], None, str]
Stmt = Union[List[Any], bool, float, int, Dict[str, Any], None, str]

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


def from_method(node):
    return f"from_{node.__class__.__name__}"


def from_this(cls, node):
    return getattr(cls, from_method(node))(node)


def build_expr_list(nodes):
    expr_list = []
    for expr_node in nodes:
        method = from_method(expr_node)
        for expr_type in _EXPR_TYPES:
            if hasattr(expr_type, method):
                expr_list.append(getattr(expr_type, method)(expr_node))
                break
        else:
            raise ValueError(f"No Expr type in {_EXPR_TYPES} with {method}: \n```\n{ast.unparse(expr_node) if expr_node else None}\n```")
    return expr_list


def build_stmt_list(nodes):
    stmt_list = []
    for stmt_node in nodes:
        method = from_method(stmt_node)
        for stmt_type in _STMT_TYPES:
            if hasattr(stmt_type, method):
                stmt_list.append(getattr(stmt_type, method)(stmt_node))
                break
        else:
            raise ValueError(f"No Stmt type in {_STMT_TYPES} with {method}: \n```\n{ast.unparse(stmt_node)}\n```")
    return stmt_list


class GoAST(ast.AST):
    _prefix = "ast."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = [f for f in self._fields if getattr(self, f, None)]

class ArrayType(GoAST):
    """An ArrayType node represents an array or slice type."""
    _fields = ('Elt', 'Len')
    """element type"""
    Elt: Expr
    """position of '['"""
    Lbrack: int
    """Ellipsis node for [...]T array types, nil for slice types"""
    Len: Expr

    def __init__(self, Elt: Expr, Lbrack: int,
                 Len: Expr, *args, **kwargs) -> None:
        self.Elt = Elt
        self.Lbrack = Lbrack
        self.Len = Len
        super().__init__(*args, **kwargs)


class AssignStmt(GoAST):
    _fields = ['Lhs', 'Rhs', 'Tok']

    """An AssignStmt node represents an assignment or a short variable declaration."""
    Lhs: List[Expr]
    Rhs: List[Expr]
    """assignment token, DEFINE"""
    Tok: int
    """position of Tok"""
    TokPos: int

    def __init__(self, Lhs: List[Expr],
                 Rhs: List[Expr], Tok: int, TokPos: int, *args,
                 **kwargs) -> None:
        self.Lhs = Lhs
        set_list_type(self.Lhs, "ast.Expr")
        self.Rhs = Rhs
        set_list_type(self.Rhs, "ast.Expr")
        self.Tok = Tok
        self.TokPos = TokPos
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Assign(cls, node: ast.Assign):
        expr_list = build_expr_list(node.targets)
        lhs = expr_list
        method = from_method(node.value)
        for expr_type in _EXPR_TYPES:
            if hasattr(expr_type, method):
                rhs = getattr(expr_type, method)(node.value)
                break
        else:
            raise ValueError(f"No Expr type in {_EXPR_TYPES} with {method}")
        return cls(lhs, [rhs], token.DEFINE, 0)


class BadDecl(GoAST):
    """A BadDecl node is a placeholder for declarations containing syntax errors for which no
    correct declaration nodes can be created.
    """
    _fields = tuple()
    From: int
    To: int

    def __init__(self, From: int, To: int, *args, **kwargs) -> None:
        self.From = From
        self.To = To
        super().__init__(*args, **kwargs)


class BadExpr(GoAST):
    """A BadExpr node is a placeholder for expressions containing syntax errors for which no
    correct expression nodes can be created.
    """
    _fields = tuple()
    From: int
    To: int

    def __init__(self, From: int, To: int, *args, **kwargs) -> None:
        self.From = From
        self.To = To
        super().__init__(*args, **kwargs)


class BadStmt(GoAST):
    """A BadStmt node is a placeholder for statements containing syntax errors for which no
    correct statement nodes can be created.
    """
    _fields = tuple()
    From: int
    To: int

    def __init__(self, From: int, To: int, *args, **kwargs) -> None:
        self.From = From
        self.To = To
        super().__init__(*args, **kwargs)


class BasicLit(GoAST):
    """A BasicLit node represents a literal of basic type.

    field tag; or nil

    import path
    """
    _fields = ('Kind', 'Value')
    """token.INT, token.FLOAT, token.IMAG, token.CHAR, or token.STRING"""
    Kind: int
    """literal string; e.g. 42, 0x7f, 3.14, 1e-9, 2.4i, 'a', '⧵x7f', 'foo' or '⧵m⧵n⧵o'"""
    Value: str
    """literal position"""
    ValuePos: int

    def __init__(self, Kind: int, Value: str, ValuePos: int, *args, **kwargs) -> None:
        self.Kind = Kind
        self.Value = json.dumps(Value)
        self.ValuePos = ValuePos
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Constant(cls, node: ast.Constant):
        kind = None
        t = type(node.value)
        if t == int:
            kind = token.INT
        elif t == float:
            kind = token.FLOAT
        elif t == str:
            kind = token.STRING
        elif t == complex:
            kind = token.IMAG
        else:
            raise NotImplementedError(node)
        return cls(kind, node.value, 0)


class BinaryExpr(GoAST):
    """A BinaryExpr node represents a binary expression."""
    _fields = ("Op", "X", "Y")
    """operator"""
    Op: int
    """position of Op"""
    OpPos: int
    """left operand"""
    X: Expr
    """right operand"""
    Y: Expr

    def __init__(self, Op: int, OpPos: int, X: Expr,
                 Y: Expr, *args, **kwargs) -> None:
        self.Op = Op
        self.OpPos = OpPos
        self.X = X
        self.Y = Y
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Compare(cls, node: ast.Compare):
        if len(node.ops) != 1:
            raise NotImplementedError("Op count != 1", node.ops)
        if len(node.comparators) != 1:
            raise NotImplementedError("Comparator count != 1", node.comparators)
        py_op = node.ops[0]
        node_right = node.comparators[0]
        if isinstance(py_op, ast.Gt):
            op = token.GTR
        elif isinstance(py_op, ast.GtE):
            op = token.GEQ
        elif isinstance(py_op, ast.Lt):
            op = token.LSS
        elif isinstance(py_op, ast.LtE):
            op = token.LEQ
        elif isinstance(py_op, ast.Eq):
            op = token.EQL
        elif isinstance(py_op, ast.NotEq):
            op = token.NEQ
        else:
            raise NotImplementedError(f"Unimplemented comparator: {py_op}")

        X = build_expr_list([node.left])[0]
        Y = build_expr_list([node_right])[0]
        return cls(op, 0, X, Y)

    @classmethod
    def from_BinOp(cls, node: ast.BinOp):
        py_op = node.op
        if isinstance(py_op, ast.Add):
            op = token.ADD
        elif isinstance(py_op, ast.Sub):
            op = token.SUB
        elif isinstance(py_op, ast.Mult):
            op = token.MUL
        elif isinstance(py_op, ast.Div) or isinstance(ast.FloorDiv):
            op = token.QUO
        elif isinstance(py_op, ast.Mod):
            op = token.REM
        elif isinstance(py_op, ast.And):
            op = token.LAND
        elif isinstance(py_op, ast.BitAnd):
            op = token.AND
        elif isinstance(py_op, ast.Or):
            op = token.LOR
        elif isinstance(py_op, ast.BitOr):
            op = token.OR
        elif isinstance(py_op, ast.BitXor):
            op = token.XOR
        elif isinstance(py_op, ast.LShift):
            op = token.SHL
        elif isinstance(py_op, ast.RShift):
            op = token.SHR
        # elif isinstance(py_op, ...):
        #     op = token.AND_NOT
        else:
            raise NotImplementedError(f"Unimplemented binop: {py_op}")

        X = build_expr_list([node.left])[0]
        Y = build_expr_list([node.right])[0]
        return cls(op, 0, X, Y)


class BlockStmt(GoAST):
    """A BlockStmt node represents a braced statement list.

    function body; or nil for external (non-Go) function

    function body

    CommClauses only

    CaseClauses only
    """
    _fields = ("List",)
    """position of '{'"""
    Lbrace: int
    List: List[Expr]
    """position of '}', if any (may be absent due to syntax error)"""
    Rbrace: int

    def __init__(self, Lbrace: int, List: List[Expr],
                 Rbrace: int, *args, **kwargs) -> None:
        self.Lbrace = Lbrace
        self.List = List
        set_list_type(self.List, "ast.Stmt")
        self.Rbrace = Rbrace
        super().__init__(*args, **kwargs)

    @classmethod
    def from_list(cls, node_list):
        stmts = build_stmt_list(node_list)
        return cls(0, stmts, 0)


class Object(GoAST):
    """denoted object; or nil

    Objects An Object describes a named language entity such as a package, constant, type,
    variable, function (incl. methods), or label.  The Data fields contains object-specific
    data:  Kind    Data type         Data value Pkg     *Scope            package scope
    Con     int               iota for the respective declaration
    """
    _fields = ("Data", "Decl", "Kind", "Name", "Type")
    """object-specific data; or nil"""
    Data: Expr
    """corresponding Field, XxxSpec, FuncDecl, LabeledStmt, AssignStmt, Scope; or nil"""
    Decl: Expr
    Kind: int
    """declared name"""
    Name: str
    """placeholder for type information; may be nil"""
    Type: Expr

    def __init__(self, Data: Expr,
                 Decl: Expr, Kind: int, Name: str,
                 Type: Expr, *args, **kwargs) -> None:
        self.Data = Data
        self.Decl = Decl
        self.Kind = Kind
        self.Name = Name
        self.Type = Type
        super().__init__(*args, **kwargs)


class Ident(GoAST):
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

    def __init__(self, Name: str, NamePos: int, Obj: Object, *args, **kwargs) -> None:
        self.Name = Name
        self.NamePos = NamePos
        self.Obj = Obj
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Name(cls, name: ast.Name):
        return cls.from_str(name.id)

    @classmethod
    def from_str(cls, name: str):
        return cls(name, 0, None)


class BranchStmt(GoAST):
    """A BranchStmt node represents a break, continue, goto, or fallthrough statement."""
    _fields = ("Label", "Tok")
    """label name; or nil"""
    Label: Ident
    """keyword token (BREAK, CONTINUE, GOTO, FALLTHROUGH)"""
    Tok: int
    """position of Tok"""
    TokPos: int

    def __init__(self, Label: Ident, Tok: int, TokPos: int, *args, **kwargs) -> None:
        self.Label = Label
        self.Tok = Tok
        self.TokPos = TokPos
        super().__init__(*args, **kwargs)


class CallExpr(GoAST):
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

    def __init__(self, Args: List[Expr], Ellipsis: int,
                 Fun: Expr, Lparen: int, Rparen: int, *args,
                 **kwargs) -> None:
        self.Args = Args
        set_list_type(Args, "ast.Expr")
        self.Ellipsis = Ellipsis
        self.Fun = Fun
        self.Lparen = Lparen
        self.Rparen = Rparen
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Call(cls, node: ast.Call):
        args = build_expr_list(node.args)
        ellipsis = None
        fun = build_expr_list([node.func])[0]
        return cls(args, ellipsis, fun, 0, 0)


class CaseClause(GoAST):
    """A CaseClause represents a case of an expression or type switch statement."""
    _fields = ("Body", "List")
    """statement list; or nil"""
    Body: List[Expr]
    """position of 'case' or 'default' keyword"""
    Case: int
    """position of ':'"""
    Colon: int
    """list of expressions or types; nil means default case"""
    List: List[Expr]

    def __init__(self, Body: List[Expr], Case: int, Colon: int,
                 List: List[Expr], *args, **kwargs) -> None:
        self.Body = Body
        self.Case = Case
        self.Colon = Colon
        self.List = List
        super().__init__(*args, **kwargs)


class ChanType(GoAST):
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

    def __init__(self, Arrow: int, Begin: int, Dir: int,
                 Value: Expr, *args, **kwargs) -> None:
        self.Arrow = Arrow
        self.Begin = Begin
        self.Dir = Dir
        self.Value = Value
        super().__init__(*args, **kwargs)


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

    def __init__(self, Body: List[Expr], Case: int, Colon: int,
                 Comm: Expr, *args, **kwargs) -> None:
        self.Body = Body
        self.Case = Case
        self.Colon = Colon
        self.Comm = Comm
        super().__init__(*args, **kwargs)


class Comment(GoAST):
    """Comments A Comment node represents a single //-style or /*-style comment."""
    _fields = ("Text",)
    """position of '/' starting the comment"""
    Slash: int
    """comment text (excluding '⧵n' for //-style comments)"""
    Text: str

    def __init__(self, Slash: int, Text: str, *args, **kwargs) -> None:
        self.Slash = Slash
        self.Text = Text
        super().__init__(*args, **kwargs)


class CommentGroup(GoAST):
    """A CommentGroup represents a sequence of comments with no other tokens and no empty lines
    between.

    line comments; or nil

    associated documentation; or nil
    """
    _fields = ("List",)
    """len(List) > 0"""
    List: List[Comment]

    def __init__(self, List: List[Comment], *args, **kwargs) -> None:
        self.List = List
        super().__init__(*args, **kwargs)


class CompositeLit(GoAST):
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

    def __init__(self, Elts: List[Expr], Incomplete: bool,
                 Lbrace: int, Rbrace: int, Type: Expr, *args,
                 **kwargs) -> None:
        self.Elts = Elts
        self.Incomplete = Incomplete
        self.Lbrace = Lbrace
        self.Rbrace = Rbrace
        self.Type = Type
        super().__init__(*args, **kwargs)


class DeclStmt(GoAST):
    """A DeclStmt node represents a declaration in a statement list."""
    _fields = ("Decl",)
    """*GenDecl with CONST, TYPE, or VAR token"""
    Decl: Expr

    def __init__(self, Decl: Expr, *args, **kwargs) -> None:
        self.Decl = Decl
        super().__init__(*args, **kwargs)


class DeferStmt(GoAST):
    """A DeferStmt node represents a defer statement."""
    _fields = ("Call",)
    Call: CallExpr
    """position of 'defer' keyword"""
    Defer: int

    def __init__(self, Call: CallExpr, Defer: int, *args, **kwargs) -> None:
        self.Call = Call
        self.Defer = Defer
        super().__init__(*args, **kwargs)


class Ellipsis(GoAST):
    """An Ellipsis node stands for the '...' type in a parameter list or the '...' length in an
    array type.
    """
    _fields = ("Ellipsis", "Elt")
    """position of '...'"""
    Ellipsis: int
    """ellipsis element type (parameter lists only); or nil"""
    Elt: Expr

    def __init__(self, _Ellipsis: int, Elt: Expr, *args,
                 **kwargs) -> None:
        self.Ellipsis = _Ellipsis
        self.Elt = Elt
        super().__init__(*args, **kwargs)


class EmptyStmt(GoAST):
    """An EmptyStmt node represents an empty statement. The 'position' of the empty statement is
    the position of the immediately following (explicit or implicit) semicolon.
    """
    _fields = ("Implicit", "Semicolon")
    """if set, ';' was omitted in the source"""
    Implicit: bool
    """position of following ';'"""
    Semicolon: int

    def __init__(self, Implicit: bool, Semicolon: int, *args, **kwargs) -> None:
        self.Implicit = Implicit
        self.Semicolon = Semicolon
        super().__init__(*args, **kwargs)


class ExprStmt(GoAST):
    """An ExprStmt node represents a (stand-alone) expression in a statement list."""
    _fields = ("X",)
    """expression"""
    X: Expr

    def __init__(self, X: Expr, *args, **kwargs) -> None:
        self.X = X
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Expr(cls, node: ast.Expr):
        return cls(build_expr_list([node.value])[0])


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

    def __init__(self, Comment: CommentGroup, Doc: CommentGroup, Names: List[Ident], Tag: BasicLit,
                 Type: Expr, *args, **kwargs) -> None:
        self.Comment = Comment
        self.Doc = Doc
        self.Names = Names
        set_list_type(Names, "*ast.Ident")
        self.Tag = Tag
        self.Type = Type
        super().__init__(*args, **kwargs)

    @classmethod
    def from_arg(cls, node: ast.arg):
        return cls(None, None, [from_this(Ident, node.arg)], None, build_expr_list([node.annotation])[0]
        if node.annotation else Ident.from_str("missing"))

    @classmethod
    def from_Name(cls, node: ast.Name):
        return cls(None, None, [], None, from_this(Ident, node))



class FieldList(GoAST):
    """A FieldList represents a list of Fields, enclosed by parentheses or braces.

    receiver (methods); or nil (functions)

    (incoming) parameters; non-nil

    (outgoing) results; or nil

    list of methods

    list of field declarations
    """
    _fields = ("Closing", "List", "Opening")
    """position of closing parenthesis/brace, if any"""
    Closing: int
    """field list; or nil"""
    List: List[Field]
    """position of opening parenthesis/brace, if any"""
    Opening: int

    def __init__(self, Closing: int, List: List[Field], Opening: int, *args, **kwargs) -> None:
        self.Closing = Closing
        self.List = List
        set_list_type(self.List, "*ast.Field")
        self.Opening = Opening
        super().__init__(*args, **kwargs)

    @classmethod
    def from_arguments(cls, node: ast.arguments):
        fields = []
        for arg in node.args:
            fields.append(from_this(Field, arg))
        return cls(0, fields, 0)

    @classmethod
    def from_Name(cls, node: ast.Name):
        return cls(0, [from_this(Field, node)], 0)


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

    def __init__(self, Comment: CommentGroup, Doc: CommentGroup, EndPos: int, Name: Ident, Path: BasicLit, *args,
                 **kwargs) -> None:
        self.Comment = Comment
        self.Doc = Doc
        self.EndPos = EndPos
        self.Name = Name
        self.Path = Path
        super().__init__(*args, **kwargs)


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

    def __init__(self, Objects: Dict[str, Object], Outer: 'Scope', *args, **kwargs) -> None:
        self.Objects = Objects
        self.Outer = Outer
        super().__init__(*args, **kwargs)


class File(GoAST):
    """Files and packages A File node represents a Go source file. The Comments list contains
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

    def __init__(self, Comments: List[CommentGroup],
                 Decls: List[Expr], Doc: CommentGroup,
                 Imports: List[ImportSpec], Name: Ident, Package: int, Scope: Scope, Unresolved: List[Ident], *args,
                 **kwargs) -> None:
        self.Comments = Comments
        set_list_type(self.Comments, "ast.CommentGroup")
        self.Decls = Decls
        set_list_type(self.Decls, "ast.Decl")
        self.Doc = Doc
        self.Imports = Imports
        set_list_type(self.Imports, "*ast.ImportSpec")
        self.Name = Name
        self.Package = Package
        self.Scope = Scope
        self.Unresolved = Unresolved
        set_list_type(self.Unresolved, "ast.Ident")
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Module(cls, node: ast.Module):
        decls = []
        for decl_node in node.body:
            method = from_method(decl_node)
            for decl_type in _DECL_TYPES:
                if hasattr(decl_type, method):
                    decls.append(getattr(decl_type, method)(decl_node))
                    break
            else:
                raise ValueError(f"No Decl type in {_DECL_TYPES} with {method}")
        return cls([], decls, None, [], Ident("main", 0, None), 1, None, [])


class ForStmt(GoAST):
    _fields = ("Body", "Cond", "Init", "Post")
    """A ForStmt represents a for statement."""
    Body: BlockStmt
    """condition; or nil"""
    Cond: Expr
    """position of 'for' keyword"""
    For: int
    """initialization statement; or nil"""
    Init: Expr
    """post iteration statement; or nil"""
    Post: Expr

    def __init__(self, Body: BlockStmt, Cond: Expr, For: int,
                 Init: Expr,
                 Post: Expr, *args, **kwargs) -> None:
        self.Body = Body
        self.Cond = Cond
        self.For = For
        self.Init = Init
        self.Post = Post
        super().__init__(*args, **kwargs)


class FuncType(GoAST):
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

    def __init__(self, Func: int, Params: FieldList, Results: FieldList, *args, **kwargs) -> None:
        self.Func = Func
        self.Params = Params
        self.Results = Results
        super().__init__(*args, **kwargs)

    @classmethod
    def from_FunctionDef(cls, node: ast.FunctionDef):
        params = from_this(FieldList, node.args)
        results = from_this(FieldList, node.returns) if node.returns else None
        return cls(0, params, results)


class FuncDecl(GoAST):
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

    def __init__(self, Body: BlockStmt, Doc: CommentGroup, Name: Ident, Recv: FieldList, Type: FuncType, *args,
                 **kwargs) -> None:
        self.Body = Body
        self.Doc = Doc
        self.Name = Name
        self.Recv = Recv
        self.Type = Type
        super().__init__(*args, **kwargs)

    @classmethod
    def from_FunctionDef(cls, node: ast.FunctionDef):
        body = from_this(BlockStmt, node.body)
        doc = None
        name = from_this(Ident, node.name)
        recv = None
        _type = from_this(FuncType, node)
        return cls(body, doc, name, recv, _type)

    @classmethod
    def from_If(cls, node: ast.If):
        body = from_this(BlockStmt, [node])
        doc = None
        name = from_this(Ident, "_")
        recv = None
        _type = FuncType(0, FieldList(0, [], 0), FieldList(0, [], 0))
        return cls(body, doc, name, recv, _type)


class FuncLit(GoAST):
    """A FuncLit node represents a function literal."""
    _fields = ("Body", "Type")
    """function body"""
    Body: BlockStmt
    """function type"""
    Type: FuncType

    def __init__(self, Body: BlockStmt, Type: FuncType, *args, **kwargs) -> None:
        self.Body = Body
        self.Type = Type
        super().__init__(*args, **kwargs)


class GenDecl(GoAST):
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
    Tok: int
    """position of Tok"""
    TokPos: int

    def __init__(self, Doc: CommentGroup, Lparen: int, Rparen: int,
                 Specs: List[Expr], Tok: int, TokPos: int,
                 *args, **kwargs) -> None:
        self.Doc = Doc
        self.Lparen = Lparen
        self.Rparen = Rparen
        self.Specs = Specs
        self.Tok = Tok
        self.TokPos = TokPos
        super().__init__(*args, **kwargs)


class GoStmt(GoAST):
    """A GoStmt node represents a go statement."""
    _fields = ("Call",)
    Call: CallExpr
    """position of 'go' keyword"""
    Go: int

    def __init__(self, Call: CallExpr, Go: int, *args, **kwargs) -> None:
        self.Call = Call
        self.Go = Go
        super().__init__(*args, **kwargs)


class IfStmt(GoAST):
    """An IfStmt node represents an if statement."""
    _fields = ("Body", "Cond", "Else", "Init")
    Body: BlockStmt
    """condition"""
    Cond: Expr
    """else branch; or nil"""
    Else: Stmt
    """position of 'if' keyword"""
    If: int
    """initialization statement; or nil"""
    Init: Expr

    def __init__(self, Body: BlockStmt, Cond: Expr,
                 Else: Stmt, If: int,
                 Init: Expr, *args, **kwargs) -> None:
        self.Body = Body
        self.Cond = Cond
        self.Else = Else
        self.If = If
        self.Init = Init
        super().__init__(*args, **kwargs)

    @classmethod
    def from_If(cls, node: ast.If):
        body = from_this(BlockStmt, node.body)
        cond = build_expr_list([node.test])[0]
        if len(node.orelse) == 1:
            _else = build_stmt_list(node.orelse)[0] if node.orelse else None
        elif len(node.orelse) == 0:
            _else = None
        else:
            raise NotImplementedError(f"Multiple else: {node.orelse}")
        init = None
        return cls(body, cond, _else, 0, init)
        

class IncDecStmt(GoAST):
    """An IncDecStmt node represents an increment or decrement statement."""
    _fields = ("Tok", "X")
    """INC or DEC"""
    Tok: int
    """position of Tok"""
    TokPos: int
    X: Expr

    def __init__(self, Tok: int, TokPos: int, X: Expr, *args,
                 **kwargs) -> None:
        self.Tok = Tok
        self.TokPos = TokPos
        self.X = X
        super().__init__(*args, **kwargs)


class IndexExpr(GoAST):
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

    def __init__(self, Index: Expr, Lbrack: int, Rbrack: int,
                 X: Expr, *args, **kwargs) -> None:
        self.Index = Index
        self.Lbrack = Lbrack
        self.Rbrack = Rbrack
        self.X = X
        super().__init__(*args, **kwargs)


class InterfaceType(GoAST):
    """An InterfaceType node represents an interface type."""
    _fields = ("Incomplete", "Methods")
    """true if (source) methods are missing in the Methods list"""
    Incomplete: bool
    """position of 'interface' keyword"""
    Interface: int
    """list of methods"""
    Methods: FieldList

    def __init__(self, Incomplete: bool, Interface: int, Methods: FieldList, *args, **kwargs) -> None:
        self.Incomplete = Incomplete
        self.Interface = Interface
        self.Methods = Methods
        super().__init__(*args, **kwargs)


class KeyValueExpr(GoAST):
    """A KeyValueExpr node represents (key : value) pairs in composite literals."""
    _fields = ("Key", "Value")
    """position of ':'"""
    Colon: int
    Key: Expr
    Value: Expr

    def __init__(self, Colon: int, Key: Expr,
                 Value: Expr, *args, **kwargs) -> None:
        self.Colon = Colon
        self.Key = Key
        self.Value = Value
        super().__init__(*args, **kwargs)


class LabeledStmt(GoAST):
    """A LabeledStmt node represents a labeled statement."""
    _fields = ("Label", "Stmt")
    """position of ':'"""
    Colon: int
    Label: Ident
    Stmt: Expr

    def __init__(self, Colon: int, Label: Ident, Stmt: Expr,
                 *args, **kwargs) -> None:
        self.Colon = Colon
        self.Label = Label
        self.Stmt = Stmt
        super().__init__(*args, **kwargs)


class MapType(GoAST):
    """A MapType node represents a map type."""
    _fields = ("Key", "Value")
    Key: Expr
    """position of 'map' keyword"""
    Map: int
    Value: Expr

    def __init__(self, Key: Expr, Map: int,
                 Value: Expr, *args, **kwargs) -> None:
        self.Key = Key
        self.Map = Map
        self.Value = Value
        super().__init__(*args, **kwargs)


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

    def __init__(self, Files: Dict[str, File], Imports: Dict[str, Object], Name: str, Scope: Scope, *args,
                 **kwargs) -> None:
        self.Files = Files
        self.Imports = Imports
        self.Name = Name
        self.Scope = Scope
        super().__init__(*args, **kwargs)


class ParenExpr(GoAST):
    """A ParenExpr node represents a parenthesized expression."""
    _fields = ("X",)
    """position of '('"""
    Lparen: int
    """position of ')'"""
    Rparen: int
    """parenthesized expression"""
    X: Expr

    def __init__(self, Lparen: int, Rparen: int, X: Expr,
                 *args, **kwargs) -> None:
        self.Lparen = Lparen
        self.Rparen = Rparen
        self.X = X
        super().__init__(*args, **kwargs)


class RangeStmt(GoAST):
    """A RangeStmt represents a for statement with a range clause."""
    _fields = ("Body", "Key", "Tok", "Value", "X")
    Body: BlockStmt
    """position of 'for' keyword"""
    For: int
    Key: Expr
    """ILLEGAL if Key == nil, ASSIGN, DEFINE"""
    Tok: int
    """position of Tok; invalid if Key == nil"""
    TokPos: int
    Value: Expr
    """value to range over"""
    X: Expr

    def __init__(self, Body: BlockStmt, For: int, Key: Expr,
                 Tok: int, TokPos: int, Value: Expr,
                 X: Expr, *args, **kwargs) -> None:
        self.Body = Body
        self.For = For
        self.Key = Key
        self.Tok = Tok
        self.TokPos = TokPos
        self.Value = Value
        self.X = X
        super().__init__(*args, **kwargs)


class ReturnStmt(GoAST):
    """A ReturnStmt node represents a return statement."""
    _fields = ("Results",)
    """result expressions; or nil"""
    Results: List[Expr]
    """position of 'return' keyword"""
    Return: int

    def __init__(self, Results: List[Expr], Return: int, *args,
                 **kwargs) -> None:
        self.Results = Results
        set_list_type(Results, "ast.Expr")
        self.Return = Return
        super().__init__(*args, **kwargs)

    @classmethod
    def from_Return(cls, node: ast.Return):
        return cls(build_expr_list([node.value]), 0)


class SelectStmt(GoAST):
    """A SelectStmt node represents a select statement."""
    _fields = ("Body",)
    """CommClauses only"""
    Body: BlockStmt
    """position of 'select' keyword"""
    Select: int

    def __init__(self, Body: BlockStmt, Select: int, *args, **kwargs) -> None:
        self.Body = Body
        self.Select = Select
        super().__init__(*args, **kwargs)


class SelectorExpr(GoAST):
    """A SelectorExpr node represents an expression followed by a selector."""
    _fields = ("Sel", "X",)
    """field selector"""
    Sel: Ident
    """expression"""
    X: Expr

    def __init__(self, Sel: Ident, X: Expr, *args,
                 **kwargs) -> None:
        self.Sel = Sel
        self.X = X
        super().__init__(*args, **kwargs)


class SendStmt(GoAST):
    """A SendStmt node represents a send statement."""
    _fields = ("Chan", "Value")
    """position of '<-'"""
    Arrow: int
    Chan: Expr
    Value: Expr

    def __init__(self, Arrow: int, Chan: Expr,
                 Value: Expr, *args, **kwargs) -> None:
        self.Arrow = Arrow
        self.Chan = Chan
        self.Value = Value
        super().__init__(*args, **kwargs)


class SliceExpr(GoAST):
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

    def __init__(self, High: Expr, Lbrack: int,
                 Low: Expr,
                 Max: Expr, Rbrack: int, Slice3: bool,
                 X: Expr, *args, **kwargs) -> None:
        self.High = High
        self.Lbrack = Lbrack
        self.Low = Low
        self.Max = Max
        self.Rbrack = Rbrack
        self.Slice3 = Slice3
        self.X = X
        super().__init__(*args, **kwargs)


class StarExpr(GoAST):
    """A StarExpr node represents an expression of the form '*' Expression. Semantically it
    could be a unary '*' expression, or a pointer type.
    """
    _fields = ("Star", "X")
    """position of '*'"""
    Star: int
    """operand"""
    X: Expr

    def __init__(self, Star: int, X: Expr, *args,
                 **kwargs) -> None:
        self.Star = Star
        self.X = X
        super().__init__(*args, **kwargs)


class StructType(GoAST):
    """A StructType node represents a struct type."""
    _fields = ("Fields", "Incomplete")
    """list of field declarations"""
    Fields: FieldList
    """true if (source) fields are missing in the Fields list"""
    Incomplete: bool
    """position of 'struct' keyword"""
    Struct: int

    def __init__(self, Fields: FieldList, Incomplete: bool, Struct: int, *args, **kwargs) -> None:
        self.Fields = Fields
        self.Incomplete = Incomplete
        self.Struct = Struct
        super().__init__(*args, **kwargs)


class SwitchStmt(GoAST):
    """A SwitchStmt node represents an expression switch statement."""
    _fields = ("Body", "Init", "Tag")
    """CaseClauses only"""
    Body: BlockStmt
    """initialization statement; or nil"""
    Init: Expr
    """position of 'switch' keyword"""
    Switch: int
    """tag expression; or nil"""
    Tag: Expr

    def __init__(self, Body: BlockStmt, Init: Expr,
                 Switch: int, Tag: Expr, *args,
                 **kwargs) -> None:
        self.Body = Body
        self.Init = Init
        self.Switch = Switch
        self.Tag = Tag
        super().__init__(*args, **kwargs)


class TypeAssertExpr(GoAST):
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

    def __init__(self, Lparen: int, Rparen: int, Type: Expr,
                 X: Expr, *args, **kwargs) -> None:
        self.Lparen = Lparen
        self.Rparen = Rparen
        self.Type = Type
        self.X = X
        super().__init__(*args, **kwargs)


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

    def __init__(self, Assign: int, Comment: CommentGroup, Doc: CommentGroup, Name: Ident,
                 Type: Expr, *args, **kwargs) -> None:
        self.Assign = Assign
        self.Comment = Comment
        self.Doc = Doc
        self.Name = Name
        self.Type = Type
        super().__init__(*args, **kwargs)


class TypeSwitchStmt(GoAST):
    """A TypeSwitchStmt node represents a type switch statement."""
    _fields = ("Body", "Init")
    """x := y.(type) or y.(type)"""
    Assign: Expr
    """CaseClauses only"""
    Body: BlockStmt
    """initialization statement; or nil"""
    Init: Expr
    """position of 'switch' keyword"""
    Switch: int

    def __init__(self, Assign: Expr, Body: BlockStmt,
                 Init: Expr, Switch: int, *args,
                 **kwargs) -> None:
        self.Assign = Assign
        self.Body = Body
        self.Init = Init
        self.Switch = Switch
        super().__init__(*args, **kwargs)


class UnaryExpr(GoAST):
    """A UnaryExpr node represents a unary expression. Unary '*' expressions are represented via
    StarExpr nodes.
    """
    _fields = ("Op", "X")
    """operator"""
    Op: int
    """position of Op"""
    OpPos: int
    """operand"""
    X: Expr

    @classmethod
    def from_UnaryOp(cls, node: ast.UnaryOp):
        if isinstance(node.op, ast.USub):
            op = token.SUB
        elif isinstance(node.op, ast.UAdd):
            op = token.ADD
        else:
            raise ValueError(node)
        X = build_expr_list([node.operand])[0]
        return cls(op, 0, X)

    def __init__(self, Op: int, OpPos: int, X: Expr, *args,
                 **kwargs) -> None:
        self.Op = Op
        self.OpPos = OpPos
        self.X = X
        super().__init__(*args, **kwargs)


class ValueSpec(GoAST):
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

    def __init__(self, Comment: CommentGroup, Doc: CommentGroup, Names: List[Ident],
                 Type: Expr,
                 Values: List[Expr], *args, **kwargs) -> None:
        self.Comment = Comment
        self.Doc = Doc
        self.Names = Names
        self.Type = Type
        self.Values = Values
        super().__init__(*args, **kwargs)


_DECL_TYPES = [FuncDecl, GenDecl, BadDecl]
_STMT_TYPES = [globals()[x] for x in globals() if x.endswith('Stmt')]
_EXPR_TYPES = [globals()[x] for x in globals() if x.endswith('Expr') or x.endswith('Lit') or x in ['Ident', 'Ellipsis']]

# Dumping
_LIST_TYPES = {}


def get_list_type(li: list):
    return _LIST_TYPES.get(id(li), 'interface{}')


def set_list_type(li: list, typ: str):
    _LIST_TYPES[id(li)] = typ


def dump(node, annotate_fields=True, include_attributes=False, *, indent=None):
    """
    Return a formatted dump of the tree in node.  This is mainly useful for
    debugging purposes.  If annotate_fields is true (by default),
    the returned string will show the names and the values for fields.
    If annotate_fields is false, the result string will be more compact by
    omitting unambiguous field names.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    include_attributes can be set to true.  If indent is a non-negative
    integer or string, then the tree will be pretty-printed with that indent
    level. None (the default) selects the single line representation.
    """

    def _format(node, level=0):
        if indent is not None:
            level += 1
            prefix = '\n' + indent * level
            sep = ',\n' + indent * level
        else:
            prefix = ''
            sep = ', '
        class_name = getattr(node, "_prefix", "") + node.__class__.__name__

        if isinstance(node, GoAST):
            cls = type(node)
            args = []
            allsimple = True
            keywords = annotate_fields
            for name in node._fields:
                try:
                    value = getattr(node, name)
                except AttributeError:
                    keywords = True
                    continue
                if value is None and getattr(cls, name, ...) is None:
                    keywords = True
                    continue
                value, simple = _format(value, level)
                allsimple = allsimple and simple
                if keywords:
                    args.append('%s: %s' % (name, value))
                else:
                    args.append(value)
            if include_attributes and node._attributes:
                for name in node._attributes:
                    try:
                        value = getattr(node, name)
                    except AttributeError:
                        continue
                    if value is None and getattr(cls, name, ...) is None:
                        continue
                    value, simple = _format(value, level)
                    allsimple = allsimple and simple
                    args.append('%s=%s' % (name, value))
            if allsimple and len(args) <= 3:
                return '%s { %s }' % ("&" + class_name, ', '.join(args)), not args
            return '%s { %s%s }' % ("&" + class_name, prefix, sep.join(args)), False
        elif isinstance(node, list):
            list_type = get_list_type(node)
            if not node:
                return f'[]{list_type} {{}}', True
            return f'[]{list_type} {{%s%s}}' % (prefix, sep.join(_format(x, level)[0] for x in node)), False
        # Prefer json.dumps over repr
        try:
            return json.dumps(node), True
        except:
            return repr(node), True

    if not isinstance(node, GoAST):
        raise TypeError('expected GoAST, got %r' % node.__class__.__name__)
    if indent is not None and not isinstance(indent, str):
        indent = ' ' * indent
    return _format(node)[0]

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


def clean_go_tree(go_tree: File):
    # Remove orphaned code left in functions titled "_"
    to_delete = []
    for decl in go_tree.Decls:
        if isinstance(decl, FuncDecl) and decl.Name.Name == '_':
            to_delete.append(decl)
    for decl in to_delete:
        go_tree.Decls.remove(decl)

    PrintToFmtPrintlnTransformer().visit(go_tree)


def unparse(go_tree: GoAST):
    clean_go_tree(go_tree)
    # XXX: Probably vulnerable to RCE if you put this on a server. Also not thread safe :D
    go_tree_string = dump(go_tree)
    compilation_code = """\
    package main

    import (
    	"go/ast"
    	"go/printer"
    	"go/token"
    	"os"
    )

    func main() {
    	tree := %s
    	fset := token.NewFileSet()
    	err := printer.Fprint(os.Stdout, fset, tree)
    	if err != nil {
    		panic(err)
    	}
    }
    """ % go_tree_string
    tmp_file = f"tmp_{uuid.uuid4().hex}.go"
    with open(tmp_file, "w") as f:
        f.write(compilation_code)
    code = _gorun(tmp_file)
    os.remove(tmp_file)
    return _gofmt(_goimport(code))

def _gorun(filename: str) -> str:
    p = Popen(["go", "run", filename], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = p.communicate()
    if err:
        return "\n".join("// " + x for x in err.decode().strip().splitlines())
    return out.decode()

def _gofmt(code: str) -> str:
    p = Popen(["gofmt", "-s"], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = p.communicate(code.encode())
    if err:
        return code + "\n" + "\n".join("// " + x for x in err.decode().strip().splitlines())
    return out.decode()


def _goimport(code: str) -> str:
    p = Popen(["goimports"], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = p.communicate(code.encode())
    if err:
        return code + "\n" + "\n".join("// " + x for x in err.decode().strip().splitlines())
    return out.decode()
