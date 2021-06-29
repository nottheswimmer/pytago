import ast
import inspect
import re
from collections import defaultdict
from enum import Enum
from typing import TYPE_CHECKING, TypeVar, List, Optional

if TYPE_CHECKING:  # pragma: no cover
    from pytago import go_ast

BINDABLES: dict['Bindable', list] = defaultdict(list)


class InfinitelySubscriptable:
    def __getitem__(self, item):
        return InfinitelySubscriptable()


PytagoInterfaceType = InfinitelySubscriptable()  # InterfaceType[x] to be replaced with the type of x if available
PytagoStarExpr = InfinitelySubscriptable()  # x => *x for types in fields

# Special identifiers can go here
PYTAGO_EMPTY_STRUCT = None  # struct{}{}
PYTAGO_RUNE = None  # "c" => 'c'
PYTAGO_NOSNIPPET = None  # Avoid recursion
PYTAGO_INIT = None  # Add a unique init() call to the top

class BindType(Enum):
    PARAMLESS_FUNC_LIT = 0
    FUNC_LIT = 1
    EXPR = 2
    STMT = 3


class Bindable:
    def __init__(self, f: callable, name: str,
                 bind_type: BindType,
                 deref_args: Optional[List[str]]=None,
                 results: Optional[List[str]]=None):
        self.f = f
        self.name = name
        self.bind_type = bind_type
        self.deref_args = deref_args or []
        self.results = results or []

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
    def add(cls, name, bind_type=BindType.PARAMLESS_FUNC_LIT, **kwargs):
        def inner(f):
            BINDABLES[name].append(cls(f, name, bind_type, **kwargs))
            return f

        return inner

    def bind(self, *args, kwargs=None):
        # Raises TypeError on failure
        if kwargs:
            kwargs = {k.arg: k.value for k in kwargs}
        else:
            kwargs = {}
        binding = self.sig.bind(*args, **kwargs)
        return binding

    def bind_partial(self, *args, kwargs=None):
        if kwargs:
            kwargs = {k.arg: k.value for k in kwargs}
        else:
            kwargs = {}
        return self.sig.bind_partial(*args, **kwargs)

    def binded_ast(self, binding):
        root = self.ast

        match self.bind_type:
            case BindType.PARAMLESS_FUNC_LIT | BindType.EXPR | BindType.STMT:
                class Transformer(ast.NodeTransformer):
                    def visit_arg(self, node: ast.arg):
                        if node.arg in binding.arguments or node.arg in binding.kwargs:
                            return None
                        return self.generic_visit(node)

                    def visit_Name(self, node: ast.Name):
                        self.generic_visit(node)
                        return binding.arguments.get(node.id, binding.kwargs.get(node.id, node))

                binded = Transformer().visit(root)
            case BindType.FUNC_LIT:
                class Transformer(ast.NodeTransformer):
                    def visit_FunctionDef(self, node):
                        # Only visit arguments, not the body. This helps to avoid recursion issues
                        node.args = self.generic_visit(node.args)
                        return node

                    def visit_Subscript(self, node: ast.Subscript):
                        node = self.generic_visit(node)
                        match node:
                            # Replace annotation such as PytagoInterfaceType[X] with PytagoInterfaceType[PassedArgument]
                            case ast.Subscript(slice=ast.Name()):
                                node.slice = binding.arguments.get(node.slice.id, node.slice)
                        return self.generic_visit(node)

                binded = Transformer().visit(root)
        return binded

    def binded_go_ast(self, binding):
        binded_ast = self.binded_ast(binding)

        match self.bind_type:
            case BindType.PARAMLESS_FUNC_LIT:
                from pytago.go_ast import FuncLit
                goasts = [FuncLit.from_FunctionDef(binded_ast).call()]
            case BindType.FUNC_LIT:
                from pytago.go_ast import build_expr_list, FuncLit, UnaryExpr, token

                deref = [(x in self.deref_args) for x in binding.arguments]
                _go_args = build_expr_list(binding.args)
                go_args = []
                for should_deref, arg in zip(deref, _go_args):
                    if should_deref:
                        arg = UnaryExpr(Op=token.AND, X=arg)
                    go_args.append(arg)
                goasts = FuncLit.from_FunctionDef(binded_ast, _py_context={"py_snippet": self}).call(*go_args, _py_context={"py_snippet": self})
            case BindType.EXPR:
                from pytago.go_ast import build_expr_list
                goasts = build_expr_list([getattr(x, 'value', x) for x in binded_ast.body], _py_context={"py_snippet": self})
            case BindType.STMT:
                from pytago.go_ast import build_stmt_list
                goasts = build_stmt_list(binded_ast.body)
            case _:
                raise NotImplementedError()

        if not isinstance(goasts, list):
            goasts = [goasts]

        for goast in goasts:
            if self.results:
                from pytago.go_ast import Ident
                match self.bind_type:
                    case BindType.PARAMLESS_FUNC_LIT | BindType.FUNC_LIT:
                        for field, name in zip(goast.Fun.Type.Results.List, self.results):
                            field.Names.append(Ident(name))
                    case _:
                        raise NotImplementedError()

        if len(goasts) == 1:
            return goasts[0]

        return goasts

# Built-in functions
@Bindable.add(r"int", bind_type=BindType.FUNC_LIT)
def go_int(value) -> int:  # pragma: no cover
    if isinstance(value, str):
        i, err = strconv.ParseInt(value, 10, 64)
        if err != nil:
            panic(err)
        return PYTAGO_NOSNIPPET(int)(i)
    elif isinstance(value, int):
        value
    elif isinstance(value, float):
        PYTAGO_NOSNIPPET(int)(value)


@Bindable.add(r"input", bind_type=BindType.FUNC_LIT)
def go_input() -> str:  # pragma: no cover
    text, _ = bufio.NewReader(os.Stdin).ReadString(PYTAGO_RUNE('\n'))
    return strings.ReplaceAll(text, "\n", "")


@Bindable.add(r"input", bind_type=BindType.FUNC_LIT)
def go_input(msg: str) -> str:  # pragma: no cover
    fmt.Print(msg)
    text, _ = bufio.NewReader(os.Stdin).ReadString(PYTAGO_RUNE('\n'))
    return strings.ReplaceAll(text, "\n", "")


@Bindable.add("zip")
def go_zip(a: list, b: list):  # pragma: no cover
    for i, e in enumerate(a):
        if i >= len(b):
            break
        yield e, b[i]


@Bindable.add("abs", bind_type=BindType.EXPR)
def go_abs(a: int):  # pragma: no cover
    return math.Abs(a)


@Bindable.add("map")
def go_map(f, iterable):  # pragma: no cover
    for x in iterable:
        yield f(x)


@Bindable.add("map")
def go_map_2(f, iterable1, iterable2):  # pragma: no cover
    for xy in zip(iterable1, iterable2):
        yield f(xy[0], xy[1])


@Bindable.add("filter")
def go_filter(f, iterable):  # pragma: no cover
    for x in iterable:
        if f(x):
            yield x


@Bindable.add("str", bind_type=BindType.EXPR)
def go_str(a):  # pragma: no cover
    return fmt.Sprintf("%v", a)


@Bindable.add("repr", bind_type=BindType.EXPR)
def go_repr(a):  # pragma: no cover
    return fmt.Sprintf("%#v", a)


@Bindable.add("iter")
def go_iter(a):  # pragma: no cover
    for elt in a:
        yield elt


@Bindable.add("list")
def go_list(a):  # pragma: no cover
    elts = []
    for elt in a:
        elts.append(elt)
    return elts


# List methods

# Handled via transformer
# @Bindable.add(r"(.*)\.append", bind_type=BindType.STMT)
# def go_append(X, other):  # pragma: no cover
#     X = append(X, other)

@Bindable.add(r"(.*)\.extend", bind_type=BindType.STMT)
def go_extend(X, other):  # pragma: no cover
    X = append(X, *other)


@Bindable.add(r"(.*)\.insert", bind_type=BindType.STMT)
def go_insert(s, i: int, elt):  # pragma: no cover
    s = append(s, elt)
    copy(s[i + 1:], s[i:])
    s[i] = elt


# See go_count in strings methods for count

# TODO: Sort by key and reverse sort
@Bindable.add(r"(.*)\.sort", bind_type=BindType.FUNC_LIT)
def go_sort(s):  # pragma: no cover
    if isinstance(s, list[str]):
        sort.Strings(s)
    elif isinstance(s, list[float]):
        sort.Float64s(s)
    elif isinstance(s, list[int]):
        sort.Ints(s)
    else:
        sort.Sort(s)


@Bindable.add(r"(.*)\.sort", bind_type=BindType.FUNC_LIT)
def go_sort(s, /, *, reverse=True):  # pragma: no cover
    if isinstance(s, list[str]):
        sort.Sort(sort.Reverse(sort.StringSlice(s)))
    elif isinstance(s, list[float]):
        sort.Sort(sort.Reverse(sort.Float64Slice(s)))
    elif isinstance(s, list[int]):
        sort.Sort(sort.Reverse(sort.IntSlice(s)))
    else:
        sort.Sort(sort.Reverse(s))


s = TypeVar("s")
popped = TypeVar("popped")


@Bindable.add(r"(.*)\.pop", bind_type=BindType.FUNC_LIT, deref_args=['s'])
def go_pop(s: PytagoInterfaceType[s]) -> PytagoInterfaceType[popped]:  # pragma: no cover
    i = len('*' @ s) - 1
    popped = ('*' @ s)[i]
    s @= ('*' @ s)[:i]
    return popped


# See strings methods for index
val = TypeVar("val")  # Name of each element we're searching through


@Bindable.add(r"(.*)\.remove", bind_type=BindType.FUNC_LIT, deref_args=['s'])
def go_remove(s: PytagoStarExpr[PytagoInterfaceType[s]], x: PytagoInterfaceType[val]):  # pragma: no cover
    for i, val in enumerate(('*' @ s)):
        if val == x:
            s @= append(('*' @ s)[:i], *('*' @ s)[i + 1:])
            return
    panic(errors.New("ValueError: element not found"))


@Bindable.add(r"(.*)\.pop", bind_type=BindType.FUNC_LIT, deref_args=['s'])
def go_pop(s: PytagoStarExpr[PytagoInterfaceType[s]], i: int) -> PytagoInterfaceType[popped]:  # pragma: no cover
    popped = ('*' @ s)[i]
    s @= append(('*' @ s)[:i], *('*' @ s)[i + 1:])
    return popped


@Bindable.add(r"(.*)\.clear", bind_type=BindType.STMT)
def go_clear(s: PytagoInterfaceType[s]):  # pragma: no cover
    s = nil


tmp = TypeVar("tmp")


@Bindable.add(r"(.*)\.copy", bind_type=BindType.FUNC_LIT, deref_args=['s'], results=["tmp"])
def go_copy(s) -> PytagoInterfaceType[tmp]:  # pragma: no cover
    tmp = append(tmp, *('*' @ s))
    return


# Set methods
@Bindable.add(r"(.*)\.add", bind_type=BindType.STMT)
def go_add(s, elt):  # pragma: no cover
    s[elt] = PYTAGO_EMPTY_STRUCT


s1 = TypeVar("s1")


@Bindable.add(r"(.*)\.union", bind_type=BindType.FUNC_LIT)
def go_union(s1: set, s2: set) -> PytagoInterfaceType[s1]:  # pragma: no cover
    union = set()
    for elt in s1:
        union.add(elt)
    for elt in s2:
        union.add(elt)
    return union


@Bindable.add(r"(.*)\.intersection", bind_type=BindType.FUNC_LIT)
def go_intersection(s1: set, s2: set) -> PytagoInterfaceType[s1]:  # pragma: no cover
    intersection = set()
    for elt in s1:
        if elt in s2:
            intersection.add(elt)
    return intersection


@Bindable.add(r"(.*)\.difference", bind_type=BindType.FUNC_LIT)
def go_difference(s1: set, s2: set) -> PytagoInterfaceType[s1]:  # pragma: no cover
    difference = set()
    for elt in s1:
        if elt not in s2:
            difference.add(elt)
    return difference


@Bindable.add(r"(.*)\.symmetric_difference", bind_type=BindType.FUNC_LIT)
def go_symmetric_difference(s1: set, s2: set) -> PytagoInterfaceType[s1]:  # pragma: no cover
    symmetric_difference = set()
    for elt in s1:
        if elt not in s2:
            symmetric_difference.add(elt)
    for elt in s2:
        if elt not in s1:
            symmetric_difference.add(elt)
    return symmetric_difference


@Bindable.add(r"(.*)\.issubset", bind_type=BindType.FUNC_LIT)
def go_issubset(s1: set, s2: set) -> bool:  # pragma: no cover
    for elt in s1:
        if elt not in s2:
            return False
    return True


@Bindable.add(r"(.*)\.issuperset", bind_type=BindType.FUNC_LIT)
def go_is_subset(s1: set, s2: set) -> bool:  # pragma: no cover
    for elt in s2:
        if elt not in s1:
            return False
    return True


# Dict methods

@Bindable.add(r"(.*)\.keys", bind_type=BindType.EXPR)
def go_keys(X: dict):  # pragma: no cover
    # Just remove .keys() for now, should work in some cases
    return X


@Bindable.add(r"(.*)\.update")
def go_update(d1, d2):  # pragma: no cover
    for k, v in d2.items():
        d1[k] = v


@Bindable.add(r"(.*)\.get")
def go_get_with_default(X: dict, val2, default):  # pragma: no cover
    if r := X[val2]:
        return r
    return default


# TODO: Conflict with requests.get
# @Bindable.add(r"(.*)\.get", bind_type=BindType.EXPR)
# def go_get(X: dict, val2):  # pragma: no cover
#     return X[val2]

# String methods
# TODO: Find a way to dispatch the appropriate calls for "bytes" -- e.g. bytes.ReplaceAll
#   ... maybe via transformer if we're desperate but I'd like to get away from those

@Bindable.add(r"(.*)\.capitalize", bind_type=BindType.EXPR)
def go_capitalize(s: str) -> str:  # pragma: no cover
    return s[0:1].upper() + s[1:].lower()


# TODO: casefold : issue = complicated
# TODO: center : issue = complicated

@Bindable.add(r"(.*)\.endswith", bind_type=BindType.EXPR)
def go_endswith(X: str, suffix: str) -> bool:  # pragma: no cover
    return strings.HasSuffix(X, suffix)


# TODO: expandtabs : issue = complicated

@Bindable.add(r"(.*)\.find", bind_type=BindType.EXPR)
def go_find(X: str, substr: str) -> int:  # pragma: no cover
    return strings.Index(X, substr)


@Bindable.add(r"(.*)\.find", bind_type=BindType.EXPR)
def go_find(X: str, substr: str, start: int) -> int:  # pragma: no cover
    return r + start if (r := strings.Index(X[start:], substr)) != -1 else -1


@Bindable.add(r"(.*)\.find", bind_type=BindType.EXPR)
def go_find(X: str, substr: str, start: int, end: int) -> int:  # pragma: no cover
    return r + start if (r := strings.Index(X[start:end], substr)) != -1 else -1


# TODO: format : issue = Bindable needs *args support
# TODO: format_map : issue = complicated

@Bindable.add(r"(.*)\.index", bind_type=BindType.FUNC_LIT)
def go_index(X: str, sub: str) -> int:  # pragma: no cover
    if isinstance(X, str):
        if (i := X.find(sub)) != -1:
            return i
        panic(errors.New("ValueError: substring not found"))
    elif isinstance(X, list):
        for i, val in enumerate(X):
            if val == sub:
                return i
        panic(errors.New("ValueError: element not found"))


@Bindable.add(r"(.*)\.index", bind_type=BindType.FUNC_LIT)
def go_index(X: str, sub: str, start: int) -> int:  # pragma: no cover
    if (i := X.find(sub, start)) != -1:
        return i
    panic(errors.New("ValueError: substring not found"))


@Bindable.add(r"(.*)\.index", bind_type=BindType.FUNC_LIT)
def go_index(X: str, sub: str, start: int, end: int) -> int:  # pragma: no cover
    if (i := X.find(sub, start, end)) != -1:
        return i
    panic(errors.New("ValueError: substring not found"))


@Bindable.add(r"(.*)\.isalnum", bind_type=BindType.FUNC_LIT)
def go_isalnum(X: str) -> bool:  # pragma: no cover
    for r in X:
        if not (unicode.IsLetter(r) or unicode.IsDigit(r) or unicode.IsNumber(r)):
            return False
    return True


@Bindable.add(r"(.*)\.isalpha", bind_type=BindType.FUNC_LIT)
def go_isalpha(X: str) -> bool:  # pragma: no cover
    for r in X:
        if not unicode.IsLetter(r):
            return False
    return True


@Bindable.add(r"(.*)\.isascii", bind_type=BindType.FUNC_LIT)
def go_isascii(X: str) -> bool:  # pragma: no cover
    for r in X:
        if r > unicode.MaxASCII:
            return False
    return True


# TODO: Dear god are these even right?
@Bindable.add(r"(.*)\.isdecimal", bind_type=BindType.FUNC_LIT)
def go_isdecimal(X: str) -> bool:  # pragma: no cover
    for r in X:
        if not unicode.Is(unicode.Nd, r):
            return False
    return len(X) != 0


@Bindable.add(r"(.*)\.isdigit", bind_type=BindType.FUNC_LIT)
def go_isdigit(X: str) -> bool:  # pragma: no cover
    for r in X:
        if not unicode.IsDigit(r):
            return False
    return len(X) != 0


# TODO: isidentifier

@Bindable.add(r"(.*)\.islower", bind_type=BindType.FUNC_LIT)
def go_islower(X: str) -> bool:  # pragma: no cover
    lower_found = False
    for r in X:
        if not unicode.IsLower(r):
            if not unicode.IsSpace(r):
                return False
        else:
            lower_found = True
    return lower_found and len(X) != 0


@Bindable.add(r"(.*)\.isnumeric", bind_type=BindType.FUNC_LIT)
def go_isnumeric(X: str) -> bool:  # pragma: no cover
    for r in X:
        if not (unicode.IsDigit(r) or unicode.IsNumber(r)):
            return False
    return len(X) != 0


@Bindable.add(r"(.*)\.isprintable", bind_type=BindType.FUNC_LIT)
def go_isprintable(X: str) -> bool:  # pragma: no cover
    for r in X:
        if not unicode.IsPrint(r):
            return False
    return True


@Bindable.add(r"(.*)\.isspace", bind_type=BindType.FUNC_LIT)
def go_isspace(X: str) -> bool:  # pragma: no cover
    for r in X:
        if not unicode.IsSpace(r):
            return False
    return len(X) != 0


# TODO: istitle

@Bindable.add(r"(.*)\.isupper", bind_type=BindType.FUNC_LIT)
def go_isupper(X: str) -> bool:  # pragma: no cover
    upper_found = False
    for r in X:
        if not unicode.IsUpper(r):
            if not unicode.IsSpace(r):
                return False
        else:
            upper_found = True
    return upper_found and len(X) != 0


@Bindable.add(r"(.*)\.join", bind_type=BindType.EXPR)
def go_join(sep: str, X: str) -> str:  # pragma: no cover
    return strings.Join(X, sep)


# TODO: ljust

@Bindable.add(r"(.*)\.lower", bind_type=BindType.EXPR)
def go_capitalize(s: str) -> str:  # pragma: no cover
    return strings.ToLower(s)


@Bindable.add(r"(.*)\.lstrip", bind_type=BindType.EXPR)
def go_lstrip(X: str) -> list[str]:  # pragma: no cover
    return strings.TrimLeftFunc(X, unicode.IsSpace)


@Bindable.add(r"(.*)\.lstrip", bind_type=BindType.EXPR)
def go_lstrip(X: str, cutset: list[str]) -> str:  # pragma: no cover
    return strings.TrimLeft(X, cutset)


# TODO: maketrans
# TODO: partition

@Bindable.add(r"(.*)\.removeprefix", bind_type=BindType.EXPR)
def go_removeprefix(X: str, prefix: str) -> str:  # pragma: no cover
    return strings.TrimPrefix(X, prefix)


@Bindable.add(r"(.*)\.removesuffix", bind_type=BindType.EXPR)
def go_removesuffix(X: str, suffix: str) -> str:  # pragma: no cover
    return strings.TrimSuffix(X, suffix)


@Bindable.add(r"(.*)\.replace", bind_type=BindType.EXPR)
def go_replace(X: str, old: str, new: str) -> str:  # pragma: no cover
    return strings.ReplaceAll(X, old, new)


@Bindable.add(r"(.*)\.replace", bind_type=BindType.EXPR)
def go_replace(X: str, old: str, new: str, n: int) -> str:  # pragma: no cover
    return strings.Replace(X, old, new, n)


@Bindable.add(r"(.*)\.rfind", bind_type=BindType.EXPR)
def go_rfind(X: str, sub: str) -> int:  # pragma: no cover
    return strings.LastIndex(X, sub)


@Bindable.add(r"(.*)\.rfind", bind_type=BindType.EXPR)
def go_rfind(X: str, substr: str, start: int) -> int:  # pragma: no cover
    return r + start if (r := strings.LastIndex(X[start:], substr)) != -1 else -1


@Bindable.add(r"(.*)\.rfind", bind_type=BindType.EXPR)
def go_rfind(X: str, substr: str, start: int, end: int) -> int:  # pragma: no cover
    return r + start if (r := strings.LastIndex(X[start:end], substr)) != -1 else -1


@Bindable.add(r"(.*)\.rindex", bind_type=BindType.FUNC_LIT)
def go_rindex(X: str, sub: str) -> int:  # pragma: no cover
    if (i := X.rfind(sub)) != -1:
        return i
    panic(errors.New("ValueError: substring not found"))


@Bindable.add(r"(.*)\.rindex", bind_type=BindType.FUNC_LIT)
def go_rindex(X: str, sub: str, start: int) -> int:  # pragma: no cover
    if (i := X.rfind(sub, start)) != -1:
        return i
    panic(errors.New("ValueError: substring not found"))


@Bindable.add(r"(.*)\.rindex", bind_type=BindType.FUNC_LIT)
def go_rindex(X: str, sub: str, start: int, end: int) -> int:  # pragma: no cover
    if (i := X.rfind(sub, start, end)) != -1:
        return i
    panic(errors.New("ValueError: substring not found"))


# TODO: rjust
# TODO: rsplit

@Bindable.add(r"(.*)\.rstrip", bind_type=BindType.EXPR)
def go_rstrip(X: str) -> list[str]:  # pragma: no cover
    return strings.TrimRightFunc(X, unicode.IsSpace)


@Bindable.add(r"(.*)\.rstrip", bind_type=BindType.EXPR)
def go_rstrip(X: str, cutset: list[str]) -> str:  # pragma: no cover
    return strings.TrimRight(X, cutset)


@Bindable.add(r"(.*)\.split", bind_type=BindType.EXPR)
def go_split(X: str) -> list[str]:  # pragma: no cover
    return strings.Fields(X)


@Bindable.add(r"(.*)\.split", bind_type=BindType.EXPR)
def go_split(X: str, sep: str) -> list[str]:  # pragma: no cover
    return strings.Split(X, sep)


@Bindable.add(r"(.*)\.split", bind_type=BindType.EXPR)
def go_split(X: str, sep: str, maxsplit: int) -> list[str]:  # pragma: no cover
    return strings.SplitN(X, sep, maxsplit)


@Bindable.add(r"(.*)\.splitlines", bind_type=BindType.FUNC_LIT, results=['lines'])
def go_splitlines(s: str) -> list[str]:  # pragma: no cover
    sc = bufio.NewScanner(strings.NewReader(s))
    while sc.Scan():
        lines.append(sc.Text())
    return


# TODO: splitlines w/ keepends

@Bindable.add(r"(.*)\.startswith", bind_type=BindType.EXPR)
def go_startswith(X: str, prefix: str) -> bool:  # pragma: no cover
    return strings.HasPrefix(X, prefix)


@Bindable.add(r"(.*)\.strip", bind_type=BindType.EXPR)
def go_strip(X: str) -> list[str]:  # pragma: no cover
    return strings.TrimSpace(X)


@Bindable.add(r"(.*)\.strip", bind_type=BindType.EXPR)
def go_strip(X: str, cutset: list[str]) -> str:  # pragma: no cover
    return strings.Trim(X, cutset)


@Bindable.add(r"(.*)\.title", bind_type=BindType.FUNC_LIT)
def go_title(s: str) -> str:  # pragma: no cover
    ws = True
    sb: strings.Builder
    for r in s:
        if unicode.IsSpace(r):
            ws = True
            sb.WriteRune(r)
        elif ws:
            ws = False
            sb.WriteRune(unicode.ToUpper(r))
        else:
            sb.WriteRune(unicode.ToLower(r))
    return sb.String()


# TODO: zfill


@Bindable.add(r"(.*)\.count", bind_type=BindType.FUNC_LIT)
def go_count(X: str, elt: str) -> int:  # pragma: no cover
    if isinstance(X, str):
        return strings.Count(X, elt)
    elif isinstance(X, list):  # Probably only works because it's last
        n = 0
        for v in X:
            if v == elt:
                n += 1
        return n


# TODO: migrate encode from transformer

@Bindable.add(r"(.*)\.upper", bind_type=BindType.EXPR)
def go_upper(s: str) -> str:  # pragma: no cover
    return strings.ToUpper(s)


# TODO: zfill

# JSON

@Bindable.add("json.dumps")
def go_json_dumps(m):  # pragma: no cover
    b, err = json.Marshal(m)
    if err != nil:
        panic(err)
    return string(b)


# Logging methods

@Bindable.add(r"logging\.info", bind_type=BindType.EXPR)
def go_logging_info(msg):  # pragma: no cover
    return log.Println("INFO:", msg)


@Bindable.add(r"logging\.debug", bind_type=BindType.EXPR)
def go_logging_debug(msg):  # pragma: no cover
    return log.Println("DEBUG:", msg)


@Bindable.add(r"logging\.warning", bind_type=BindType.EXPR)
def go_logging_warning(msg):  # pragma: no cover
    return log.Println("WARNING:", msg)


@Bindable.add(r"logging\.error", bind_type=BindType.EXPR)
def go_logging_error(msg):  # pragma: no cover
    return log.Println("ERROR:", msg)


# Dunder methods

@Bindable.add(r"(.*)\.__len__", bind_type=BindType.EXPR)
def go_len_dunder(X) -> int:  # pragma: no cover
    return len(X)


# Initialization and Construction

# To get called in an object's instantiation.
# @Bindable.add(r"(.*)\.__new__", bind_type=BindType.EXPR)
# def go_new_dunder(cls, other):  # pragma: no cover
#     return


# To get called by the __new__ method.
# @Bindable.add(r"(.*)\.__init__", bind_type=BindType.EXPR)
# def go_init_dunder(self, other):  # pragma: no cover
#     return


# Destructor method.
@Bindable.add(r"(.*)\.__del__", bind_type=BindType.STMT)
def go_del_dunder(self):  # pragma: no cover
    del self


# Unary operators and functions

# To get called for unary positive e.g. +someobject.
@Bindable.add(r"(.*)\.__pos__", bind_type=BindType.EXPR)
def go_pos_dunder(self):  # pragma: no cover
    return +self


# To get called for unary negative e.g. -someobject.
@Bindable.add(r"(.*)\.__neg__", bind_type=BindType.EXPR)
def go_neg_dunder(self):  # pragma: no cover
    return -self


# To get called by built-in abs() function.
@Bindable.add(r"(.*)\.__abs__", bind_type=BindType.EXPR)
def go_abs_dunder(self):  # pragma: no cover
    return abs(self)


# To get called for inversion using the ~ operator.
@Bindable.add(r"(.*)\.__invert__", bind_type=BindType.EXPR)
def go_invert_dunder(self):  # pragma: no cover
    return ~self


# To get called by built-in round() function.
@Bindable.add(r"(.*)\.__round__", bind_type=BindType.EXPR)
def go_round_dunder(self, n):  # pragma: no cover
    return round(self, n)


# To get called by built-in math.floor() function.
@Bindable.add(r"(.*)\.__floor__", bind_type=BindType.EXPR)
def go_floor_dunder(self):  # pragma: no cover
    return math.floor(self)


# To get called by built-in math.ceil() function.
@Bindable.add(r"(.*)\.__ceil__", bind_type=BindType.EXPR)
def go_ceil_dunder(self):  # pragma: no cover
    return math.ceil(self)


# To get called by built-in math.trunc() function.
@Bindable.add(r"(.*)\.__trunc__", bind_type=BindType.EXPR)
def go_trunc_dunder(self):  # pragma: no cover
    return math.trunc(self)


# Augmented Assignment

# To get called on addition with assignment e.g. a +=b.
@Bindable.add(r"(.*)\.__iadd__", bind_type=BindType.STMT)
def go_iadd_dunder(self, other):  # pragma: no cover
    self += other


# To get called on subtraction with assignment e.g. a -=b.
@Bindable.add(r"(.*)\.__isub__", bind_type=BindType.STMT)
def go_isub_dunder(self, other):  # pragma: no cover
    self -= other


# To get called on multiplication with assignment e.g. a *=b.
@Bindable.add(r"(.*)\.__imul__", bind_type=BindType.STMT)
def go_imul_dunder(self, other):  # pragma: no cover
    self *= other


# To get called on integer division with assignment e.g. a //=b.
@Bindable.add(r"(.*)\.__ifloordiv__", bind_type=BindType.STMT)
def go_ifloordiv_dunder(self, other):  # pragma: no cover
    self //= other


# To get called on division with assignment e.g. a /=b.
@Bindable.add(r"(.*)\.__idiv__", bind_type=BindType.STMT)
def go_idiv_dunder(self, other):  # pragma: no cover
    self /= other


# To get called on true division with assignment
@Bindable.add(r"(.*)\.__itruediv__", bind_type=BindType.STMT)
def go_itruediv_dunder(self, other):  # pragma: no cover
    self /= other


# To get called on modulo with assignment e.g. a%=b.
@Bindable.add(r"(.*)\.__imod__", bind_type=BindType.STMT)
def go_imod_dunder(self, other):  # pragma: no cover
    self %= other


# To get called on exponentswith assignment e.g. a **=b.
@Bindable.add(r"(.*)\.__ipow__", bind_type=BindType.STMT)
def go_ipow_dunder(self, other):  # pragma: no cover
    self **= other


# To get called on left bitwise shift with assignment e.g. a<<=b.
@Bindable.add(r"(.*)\.__ilshift__", bind_type=BindType.STMT)
def go_ilshift_dunder(self, other):  # pragma: no cover
    self <<= other


# To get called on right bitwise shift with assignment e.g. a >>=b.
@Bindable.add(r"(.*)\.__irshift__", bind_type=BindType.STMT)
def go_irshift_dunder(self, other):  # pragma: no cover
    self >>= other


# To get called on bitwise AND with assignment e.g. a&=b.
@Bindable.add(r"(.*)\.__iand__", bind_type=BindType.STMT)
def go_iand_dunder(self, other):  # pragma: no cover
    self &= other


# To get called on bitwise OR with assignment e.g. a|=b.
@Bindable.add(r"(.*)\.__ior__", bind_type=BindType.STMT)
def go_ior_dunder(self, other):  # pragma: no cover
    self |= other


# To get called on bitwise XOR with assignment e.g. a ^=b.
@Bindable.add(r"(.*)\.__ixor__", bind_type=BindType.STMT)
def go_ixor_dunder(self, other):  # pragma: no cover
    self ^= other


# Type Conversion Magic Methods

# To get called by built-in int() method to convert a type to an int.
@Bindable.add(r"(.*)\.__int__", bind_type=BindType.EXPR)
def go_int_dunder(self):  # pragma: no cover
    return int(self)


# To get called by built-in float() method to convert a type to float.
@Bindable.add(r"(.*)\.__float__", bind_type=BindType.EXPR)
def go_float_dunder(self):  # pragma: no cover
    return float(self)


# To get called by built-in complex() method to convert a type to complex.
@Bindable.add(r"(.*)\.__complex__", bind_type=BindType.EXPR)
def go_complex_dunder(self):  # pragma: no cover
    return complex(self)


# To get called by built-in oct() method to convert a type to octal.
@Bindable.add(r"(.*)\.__oct__", bind_type=BindType.EXPR)
def go_oct_dunder(self):  # pragma: no cover
    return oct(self)


# To get called by built-in hex() method to convert a type to hexadecimal.
@Bindable.add(r"(.*)\.__hex__", bind_type=BindType.EXPR)
def go_hex_dunder(self):  # pragma: no cover
    return hex(self)


# To get called on type conversion to an int when the object is used in a slice expression.
@Bindable.add(r"(.*)\.__index__", bind_type=BindType.EXPR)
def go_index_dunder(self):  # pragma: no cover
    return self


# String Magic Methods

# To get called by built-in str() method to return a string representation of a type.
@Bindable.add(r"(.*)\.__str__", bind_type=BindType.EXPR)
def go_str_dunder(self):  # pragma: no cover
    return str(self)


# To get called by built-in repr() method to return a machine readable representation of a type.
@Bindable.add(r"(.*)\.__repr__", bind_type=BindType.EXPR)
def go_repr_dunder(self):  # pragma: no cover
    return repr(self)


# To get called by built-in string.format() method to return a new style of string.
@Bindable.add(r"(.*)\.__format__", bind_type=BindType.EXPR)
def go_format_dunder(self, formatstr):  # pragma: no cover
    return self.format(formatstr)


# To get called by built-in hash() method to return an integer.
@Bindable.add(r"(.*)\.__hash__", bind_type=BindType.EXPR)
def go_hash_dunder(self):  # pragma: no cover
    return hash(self)


# To get called by built-in bool() method to return True or False.
@Bindable.add(r"(.*)\.__nonzero__", bind_type=BindType.EXPR)
def go_nonzero_dunder(self):  # pragma: no cover
    return bool(self)


# To get called by built-in dir() method to return a list of attributes of a class.
@Bindable.add(r"(.*)\.__dir__", bind_type=BindType.EXPR)
def go_dir_dunder(self):  # pragma: no cover
    return dir(self)


# To get called by built-in sys.getsizeof() method to return the size of an object.
@Bindable.add(r"(.*)\.__sizeof__", bind_type=BindType.EXPR)
def go_sizeof_dunder(self):  # pragma: no cover
    return sys.getsizeof(self)


# Attribute Magic Methods

# Is called when the accessing attribute of a class that does not exist.
# @Bindable.add(r"(.*)\.__getattr__", bind_type=BindType.EXPR)
# def go_getattr_dunder(self, name):  # pragma: no cover
#     return


# Is called when assigning a value to the attribute of a class.
# @Bindable.add(r"(.*)\.__setattr__", bind_type=BindType.EXPR)
# def go_setattr_dunder(self, name, value):  # pragma: no cover
#     return


# Is called when deleting an attribute of a class.
# @Bindable.add(r"(.*)\.__delattr__", bind_type=BindType.EXPR)
# def go_delattr_dunder(self, name):  # pragma: no cover
#     return

# Operator Magic Methods

# To get called on add operation using + operator
@Bindable.add(r"(.*)\.__add__", bind_type=BindType.EXPR)
def go_add_dunder(self, other):  # pragma: no cover
    return self + other


# To get called on subtraction operation using - operator.
@Bindable.add(r"(.*)\.__sub__", bind_type=BindType.EXPR)
def go_sub_dunder(self, other):  # pragma: no cover
    return self - other


# To get called on multiplication operation using * operator.
@Bindable.add(r"(.*)\.__mul__", bind_type=BindType.EXPR)
def go_mul_dunder(self, other):  # pragma: no cover
    return self * other


# To get called on floor division operation using // operator.
@Bindable.add(r"(.*)\.__floordiv__", bind_type=BindType.EXPR)
def go_floordiv_dunder(self, other):  # pragma: no cover
    return self // other


# To get called on division operation using / operator.
@Bindable.add(r"(.*)\.__truediv__", bind_type=BindType.EXPR)
def go_truediv_dunder(self, other):  # pragma: no cover
    return self / other


# To get called on modulo operation using % operator.
@Bindable.add(r"(.*)\.__mod__", bind_type=BindType.EXPR)
def go_mod_dunder(self, other):  # pragma: no cover
    return self % other


# To get called on calculating the power using ** operator.
@Bindable.add(r"(.*)\.__pow__", bind_type=BindType.EXPR)
def go_pow_dunder(self, other):  # pragma: no cover
    return self ** other


# To get called on comparison using < operator.
@Bindable.add(r"(.*)\.__lt__", bind_type=BindType.EXPR)
def go_lt_dunder(self, other):  # pragma: no cover
    return self < other


# To get called on comparison using <= operator.
@Bindable.add(r"(.*)\.__le__", bind_type=BindType.EXPR)
def go_le_dunder(self, other):  # pragma: no cover
    return self <= other


# To get called on comparison using == operator.
@Bindable.add(r"(.*)\.__eq__", bind_type=BindType.EXPR)
def go_eq_dunder(self, other):  # pragma: no cover
    return self == other


# To get called on comparison using != operator.
@Bindable.add(r"(.*)\.__ne__", bind_type=BindType.EXPR)
def go_ne_dunder(self, other):  # pragma: no cover
    return self != other


# To get called on comparison using >= operator.
@Bindable.add(r"(.*)\.__ge__", bind_type=BindType.EXPR)
def go_ge_dunder(self, other):  # pragma: no cover
    return self >= other


# Randomness
@Bindable.add(r"random\.random", bind_type=BindType.EXPR)
def go_random_random() -> float:  # pragma: no cover
    return rand.Float64()
    def _():
        def PYTAGO_INIT(): rand.Seed(time.Now().UnixNano())


@Bindable.add(r"random\.randrange", bind_type=BindType.EXPR)
def go_random_randrange(start: int) -> int:  # pragma: no cover
    return rand.Intn(start)
    def _():
        def PYTAGO_INIT(): rand.Seed(time.Now().UnixNano())


@Bindable.add(r"random\.randrange", bind_type=BindType.FUNC_LIT)
def go_random_randrange(start: int, stop: int) -> int:  # pragma: no cover
    n = stop - start
    return rand.Intn(n) + start
    def PYTAGO_INIT(): rand.Seed(time.Now().UnixNano())


@Bindable.add(r"random\.randint", bind_type=BindType.EXPR)
def go_random_randint(start: int, stop: int) -> int:  # pragma: no cover
    return random.randrange(start, stop + 1)
    def _():
        def PYTAGO_INIT(): rand.Seed(time.Now().UnixNano())


@Bindable.add(r"random\.choice", bind_type=BindType.EXPR)
def go_random_choice(seq) -> int:  # pragma: no cover
    return seq[rand.Intn(len(seq))]
    def _():
        def PYTAGO_INIT(): rand.Seed(time.Now().UnixNano())


@Bindable.add(r"random\.shuffle", bind_type=BindType.STMT)
def go_random_shuffle(seq):  # pragma: no cover
    def PYTAGO_INLINE(i: int, j: int):
        seq[i], seq[j] = seq[j], seq[i]
    rand.Shuffle(len(seq), PYTAGO_INLINE)
    def PYTAGO_INIT(): rand.Seed(time.Now().UnixNano())

@Bindable.add(r"random\.uniform", bind_type=BindType.FUNC_LIT)
def go_random_uniform(a: float, b: float):  # pragma: no cover
    return rand.Float64() * (b - a) + b
    def PYTAGO_INIT(): rand.Seed(time.Now().UnixNano())

# TODO: Exhaustive list of all dunders, .methods, builtins, etc implemented here...

# time methods
@Bindable.add(r"time\.sleep", bind_type=BindType.EXPR)
def go_time_sleep(duration: int):  # pragma: no cover
    return time.Sleep(duration * time.Second)


reversal = {}

# exit / quit / os.exit
@Bindable.add(r"exit", bind_type=BindType.EXPR)
def go_exit():  # pragma: no cover
    return os.Exit(0)

@Bindable.add(r"exit", bind_type=BindType.EXPR)
def go_exit(code: int):  # pragma: no cover
    return os.Exit(code)

@Bindable.add(r"quit", bind_type=BindType.EXPR)
def go_quit():  # pragma: no cover
    return os.Exit(0)

@Bindable.add(r"quit", bind_type=BindType.EXPR)
def go_quit(code: int):  # pragma: no cover
    return os.Exit(code)

@Bindable.add(r"sys\.exit", bind_type=BindType.EXPR)
def go_os_exit():  # pragma: no cover
    return os.Exit(0)

@Bindable.add(r"sys\.exit", bind_type=BindType.EXPR)
def go_os_exit(code: int):  # pragma: no cover
    return os.Exit(code)

# Handle errors on file close
@Bindable.add(r"(.*)\.close", bind_type=BindType.STMT)
def go_close(obj):
    if (err := obj.Close()) != nil:
        panic(err)


def get_node_string(node: ast.AST):
    match node:
        case ast.Name(id=x):
            s = x
        case ast.Attribute(attr=attr, value=value):
            s = get_node_string(value) + "." + attr
        case _:
            s = node.__class__.__name__
    reversal[s] = node
    return s


def get_string_node(s: str):
    if s in reversal:
        return reversal[s]
    if "." in s:
        value, attr = s.rsplit('.', 1)
        return ast.Attribute(attr=attr, value=get_string_node(value))
    return ast.Name(id=s)


def find_call_funclit(node: ast.Call) -> 'go_ast.FuncLit':
    args = node.args
    kwargs = node.keywords
    dotted = get_node_string(node.func)
    for x in BINDABLES:
        if not BINDABLES[x]:
            continue
        if match := re.fullmatch(x, dotted):
            _groups = list(match.groups() or ())
            groups = []
            while _groups:
                groups.append(get_string_node(_groups.pop(0)))

            for i, b in enumerate(BINDABLES[x].copy()):
                try:
                    binding = b.bind(*groups, *args, kwargs=kwargs)
                except TypeError as e:
                    continue

                # Removing and adding these back out of paranoia that, otherwise,
                # an argument with the name of what we're binding to could cause this
                # to infinitely recurse
                # Commented out for now because some of this has been addressed for FUNC_LIT
                # del BINDABLES[x][i]
                go_ast = b.binded_go_ast(binding)
                # BINDABLES[x].insert(i, b)
                return go_ast


if __name__ == '__main__':  # pragma: no cover
    node = ast.parse(
        """
        zip([1, 2, 3], [4, 5, 6])
        """
    ).body[0].value
    print(find_call_funclit(node))
