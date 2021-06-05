import ast
import json
from contextlib import contextmanager

from subprocess import Popen, PIPE

_PYTHON_TO_GO_TYPE_STRING = {
    int: 'int'
}

def _python_to_go_type_string(t):
    return _PYTHON_TO_GO_TYPE_STRING.get(t, t.__name__)

class Unparser(ast._Unparser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scope = dict()
        self._assigning = False
        self._assigned_type = None
        self._extra_precall_params = []
        self._subscripting = None

    # I'd like some simple support to help someone trying to understand how negative
    # indexing translates into Golang, even if it only works for constants
    def visit_Subscript(self, node):
        def is_simple_tuple(slice_value):
            # when unparsing a non-empty tuple, the parentheses can be safely
            # omitted if there aren't any elements that explicitly requires
            # parentheses (such as starred expressions).
            return (
                isinstance(slice_value, ast.Tuple)
                and slice_value.elts
                and not any(isinstance(elt, ast.Starred) for elt in slice_value.elts)
            )

        self.set_precedence(ast._Precedence.ATOM, node.value)
        self.traverse(node.value)
        was_subscripting = self._subscripting
        self._subscripting = node.value
        with self.delimit("[", "]"):
            if is_simple_tuple(node.slice):
                self.items_view(self.traverse, node.slice.elts)
            else:
                self.traverse(node.slice)
        self._subscripting = was_subscripting

    def visit_UnaryOp(self, node):
        operator = self.unop[node.op.__class__.__name__]
        operator_precedence = self.unop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            if self._subscripting and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
                self.write(f"len(")
                self.traverse(self._subscripting)
                self.write(")")

            self.write(operator)
            # factor prefixes (+, -, ~) shouldn't be seperated
            # from the value they belong, (e.g: +1 instead of + 1)
            if operator_precedence is not ast._Precedence.FACTOR:
                self.write(" ")
            self.set_precedence(operator_precedence, node.operand)
            self.traverse(node.operand)

    def write(self, text):
        """Append a piece of text"""
        if '-' in text:
            print(text)
        self._source.append(text)

    def visit_AugAssign(self, node):
        self.fill()
        list_plus_equals = self.binop[node.op.__class__.__name__] == '+' and \
                           (self.guess_type(node.target) == list or self.guess_type(node.value) == list)
        self.traverse(node.target)
        if list_plus_equals:
            self.write(" = append(")
            self.traverse(node.target)
            self.write(", ")
            self.traverse(node.value)
            self.write("...)")
        else:
            self.write(" " + self.binop[node.op.__class__.__name__] + "= ")
            self.traverse(node.value)

    def guess_type(self, node):
        try:
            return type(ast.literal_eval(node))
        except ValueError:
            pass
        if isinstance(node, ast.Name) and node.id in self._scope:
            return self._scope[node.id]
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Div):
                return float
            if isinstance(node.op, ast.FloorDiv):
                return int
            left_type = self.guess_type(node.left)
            if left_type == float:
                return float
            right_type = self.guess_type(node.right)
            if right_type == float:
                return float
            return left_type or right_type
        return None

    # Go needs := to initialize variables
    def visit_Assign(self, node):
        self.fill()
        self._assigned_type = self.guess_type(node.value)
        for target in node.targets:
            prev_assigning = self._assigning
            prev_scope_size = len(self._scope)
            self._assigning = True
            self.traverse(target)
            if len(self._scope) > prev_scope_size:
                self.write(" := ")
            else:
                self.write(" = ")
            self._assigning = prev_assigning
        self.traverse(node.value)
        if type_comment := self.get_type_comment(node):
            self.write(type_comment)

    # Go uses the keyword "func" rather than "def"
    def visit_FunctionDef(self, node):
        self._function_helper(node, "func")

    def visit_Name(self, node):
        name = {
            'print': 'fmt.Println',
        }.get(node.id, node.id)
        self.write(name)
        if self._assigning:
            self._scope[name] = self._assigned_type

    def visit_Attribute(self, node):
        self.set_precedence(ast._Precedence.ATOM, node.value)
        self.traverse(node.value)
        # Special case: 3.__abs__() is a syntax error, so if node.value
        # is an integer literal then we need to either parenthesize
        # it or add an extra space to get 3 .__abs__().
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, int):
            self.write(" ")

        if isinstance(node.value, ast.Name) and self.guess_type(node.value) == list and node.attr == 'append':
            self.write(" = ")
            self.write(node.attr)
            self._extra_precall_params.append(node.value)
        else:
            self.write(".")
            self.write(node.attr)

    def visit_Call(self, node):
        self.set_precedence(ast._Precedence.ATOM, node.func)
        self.traverse(node.func)
        with self.delimit("(", ")"):
            comma = False
            args = [*self._extra_precall_params, *node.args]
            self._extra_precall_params.clear()
            for e in args:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)
            for e in node.keywords:
                if comma:
                    self.write(", ")
                else:
                    comma = True
                self.traverse(e)

    def visit_If(self, node):
        # TODO: Integrate such blocks into the main function
        if ast.unparse(node.test) == '__name__ == \'__main__\'':
            return
        return super().visit_If(node)

    # Go doesn't have the "**" operator, so use math.Pow
    def visit_BinOp(self, node):
        operator = self.binop[node.op.__class__.__name__]
        operator_precedence = self.binop_precedence[operator]
        with self.require_parens(operator_precedence, node):
            if operator in self.binop_rassoc:
                left_precedence = operator_precedence.next()
                right_precedence = operator_precedence
            else:
                left_precedence = operator_precedence
                right_precedence = operator_precedence.next()

            left_type = self.guess_type(node.left)
            right_type = self.guess_type(node.right)
            left_prefix = ""
            left_suffix = ""
            right_prefix = ""
            right_suffix = ""
            join_string = f" {operator} "

            if operator == "**":
                left_prefix += "math.Pow("
                right_suffix = ")" + right_suffix
                join_string = ", "

            if operator == "/":
                if left_type != float:
                    left_prefix += "float64("
                    left_suffix = ")" + left_suffix
                if right_type != float:
                    right_prefix += "float64("
                    right_suffix = ")" + right_suffix
            elif operator == "//":
                join_string = " / "
                either_was_float = float in [left_type, right_type]
                if left_type != int:
                    left_prefix += "int("
                    left_suffix = ")" + left_suffix
                if right_type != int:
                    right_prefix += "int("
                    right_suffix = ")" + right_suffix
                if either_was_float:
                    left_prefix += "float64("
                    right_suffix = ")" + right_suffix
            else:
                if right_type == float and left_type != float:
                    left_prefix += "float64("
                    left_suffix = ")" + left_suffix
                elif left_type == float and right_type != float:
                    right_prefix += "float64("
                    right_suffix = ")" + right_suffix

            self.set_precedence(left_precedence, node.left)
            with self.delimit(left_prefix, left_suffix):
                self.write(left_prefix)
            self.traverse(node.left)
            self.write(join_string)
            self.set_precedence(right_precedence, node.right)
            with self.delimit(right_prefix, right_suffix):
                self.write(right_prefix)
            self.traverse(node.right)

    def visit_List(self, node):
        t = None
        for element in node.elts:
            t = self.guess_type(element)
            if t is not None:
                break
        if t:
            type_string = _python_to_go_type_string(t)
        else:
            type_string = "struct{}"
        self.write(f"[]{type_string}")
        with self.delimit("{", "}"):
            self.interleave(lambda: self.write(", "), self.traverse, node.elts)

    # Quick hack to get 99% of the string formatting functionality I want
    #   without getting into the dirty stuff for now
    def _write_constant(self, value):
        if isinstance(value, (float, complex)):
            # Substitute overflowing decimal literal for AST infinities,
            # and inf - inf for NaNs.
            self.write(
                repr(value)
                    .replace("inf", ast._INFSTR)
                    .replace("nan", f"({ast._INFSTR}-{ast._INFSTR})")
            )
        elif self._avoid_backslashes and isinstance(value, str):
            self._write_str_avoiding_backslashes(value)
        else:
            try:
                self.write(json.dumps(value))
            except:
                self.write(repr(value))

    # Go doesn't have the '->' when outputting the function type
    def visit_FunctionType(self, node):
        with self.delimit("(", ")"):
            self.interleave(
                lambda: self.write(", "), self.traverse, node.argtypes
            )

        self.traverse(node.returns)

    # Go doesn't have the ':' when specifying a param's type
    def visit_arg(self, node):
        self.write(node.arg)
        if node.annotation:
            self.write(" ")
            self.traverse(node.annotation)

    # Go doesn't have the ':' when specifying a param's type
    def visit_arguments(self, node):
        first = True
        # normal arguments
        all_args = node.posonlyargs + node.args
        defaults = [None] * (len(all_args) - len(node.defaults)) + node.defaults
        for index, elements in enumerate(zip(all_args, defaults), 1):
            a, d = elements
            if first:
                first = False
            else:
                self.write(", ")
            self.traverse(a)
            if d:
                self.write("=")
                self.traverse(d)
            if index == len(node.posonlyargs):
                self.write(", /")

        # varargs, or bare '*' if no varargs but keyword-only arguments present
        if node.vararg or node.kwonlyargs:
            if first:
                first = False
            else:
                self.write(", ")
            self.write("*")
            if node.vararg:
                self.write(node.vararg.arg)
                if node.vararg.annotation:
                    self.write(" ")
                    self.traverse(node.vararg.annotation)

        # keyword-only arguments
        if node.kwonlyargs:
            for a, d in zip(node.kwonlyargs, node.kw_defaults):
                self.write(", ")
                self.traverse(a)
                if d:
                    self.write("=")
                    self.traverse(d)

        # kwargs
        if node.kwarg:
            if first:
                first = False
            else:
                self.write(", ")
            self.write("**" + node.kwarg.arg)
            if node.kwarg.annotation:
                self.write(" ")
                self.traverse(node.kwarg.annotation)

    # Go doesn't have the '->' when outputting the function type
    def _function_helper(self, node, fill_suffix):
        self.maybe_newline()
        for deco in node.decorator_list:
            self.fill("@")
            self.traverse(deco)
        def_str = fill_suffix + " " + node.name
        self.fill(def_str)
        with self.delimit("(", ")"):
            self.traverse(node.args)
        if node.returns:
            self.traverse(node.returns)
        with self.block(extra=self.get_type_comment(node)):
            self._write_docstring_and_traverse_body(node)

    # Go uses { } for blocks, not ':'
    @contextmanager
    def block(self, *, extra=None):
        """A context manager for preparing the source for blocks. It adds
        the character '{', increases the indentation on enter and decreases
        the indentation on exit. If *extra* is given, it will be directly
        appended after the colon character. The block is followed with '}'

        We will assume, for now, that this also contains its own scope
        """
        old_scope = self._scope
        self._scope = self._scope.copy()
        self.write("{")
        if extra:
            self.write(extra)
        self._indent += 1
        yield
        self._indent -= 1
        self.write("}")
        self._scope = old_scope


def unparse(ast_obj):
    unparser = Unparser()
    return _gofmt(_goimport(f"""\
package main

{unparser.visit(ast_obj)}
"""))


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
