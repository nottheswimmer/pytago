import json
import os
import uuid
from subprocess import Popen, PIPE

from pythagoras.go_ast import GoAST, ALL_TRANSFORMS, File, get_list_type


def unparse(go_tree: GoAST, apply_transformations=True, debugging=True):
    if apply_transformations:
        clean_go_tree(go_tree)
    # XXX: Probably vulnerable to RCE if you put this on a server.
    go_tree_string = dump(go_tree, indent='   ' if debugging else None)
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
    if debugging:
        compilation_code = _gofmt(compilation_code)
    tmp_file = f"tmp_{uuid.uuid4().hex}.go"
    if debugging:
        print(f"=== Start Compilation Code ===")
        lines = compilation_code.splitlines()
        max_i_size = len(str(len(lines)+1))
        for i, line in enumerate(lines, start=1):
            print(str(i).rjust(max_i_size), line)
        print(f"=== End Compilation Code ===")
    with open(tmp_file, "w") as f:
        f.write(compilation_code)
    code = _gorun(tmp_file)
    if debugging:
        print(f"=== Start Code ===")
        print(code)
        print(f"=== End Code ===")
    os.remove(tmp_file)
    return _gofmt(_goimport(code))

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


def clean_go_tree(go_tree: File):
    for tsfm in ALL_TRANSFORMS:
        tsfm().visit(go_tree)


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
