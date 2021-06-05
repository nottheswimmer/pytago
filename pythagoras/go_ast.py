import ast
import json
from contextlib import contextmanager

from subprocess import Popen, PIPE


class Unparser(ast._Unparser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scope = set()
        self._assigning = False

    # Go needs := to initialize variables
    def visit_Assign(self, node):
        self.fill()
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
            self._scope.add(name)

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

            if operator == "**":
                self.write("math.Pow(")
                self.set_precedence(left_precedence, node.left)
                self.traverse(node.left)
                self.write(", ")
                self.set_precedence(right_precedence, node.right)
                self.traverse(node.right)
                self.write(")")
            else:
                self.set_precedence(left_precedence, node.left)
                self.traverse(node.left)
                self.write(f" {operator} ")
                self.set_precedence(right_precedence, node.right)
                self.traverse(node.right)

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
