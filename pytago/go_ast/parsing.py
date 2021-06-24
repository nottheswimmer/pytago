import json
import os
import tempfile
from subprocess import Popen, PIPE

from pytago.go_ast import GoAST, ALL_TRANSFORMS, File, get_list_type


def unparse(go_tree: GoAST, apply_transformations=True, debug=True):
    if apply_transformations:
        clean_go_tree(go_tree)
    # XXX: I can't promise this isn't vulnerable to RCE if you put this on a server.
    go_tree_string = dump(go_tree, indent='   ' if debug else None)
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
    if debug:
        compilation_code = _gofumpt(compilation_code)
    tmp_file = tempfile.NamedTemporaryFile(suffix=".go", delete=False)
    try:
        tmp_file.close()
        if debug:
            print(f"=== Start Compilation Code ===")
            lines = compilation_code.splitlines()
            max_i_size = len(str(len(lines) + 1))
            for i, line in enumerate(lines, start=1):
                print(str(i).rjust(max_i_size), line)
            print(f"=== End Compilation Code ===")
        with open(tmp_file.name, "w", encoding="utf_8") as f:
            f.write(compilation_code)
        code = _gorun(tmp_file.name)
    finally:
        os.remove(tmp_file.name)
    if debug:
        print(f"=== Start Code ===")
        print(code)
        print(f"=== End Code ===")
    externally_formatted_code = _gofumpt(_goimport(code))
    if debug:
        print(f"=== Start Externally Formatted Code ===")
        print(externally_formatted_code)
        print(f"=== End Externally Formatted Code ===")
    return externally_formatted_code


def dump(node, annotate_fields=True, include_attributes=False, *, indent=None):
    """
    Return a formatted dump of the tree in node. If annotate_fields is true (by default),
    the returned string will show the names and the values for fields.
    If annotate_fields is false, the result string will be more compact by
    omitting unambiguous field names.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    include_attributes can be set to true. If indent is a non-negative
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
            node.remove_falsy_fields()
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
            return json.dumps(node, ensure_ascii=False), True
        except:
            return repr(node), True

    if not isinstance(node, GoAST):
        raise TypeError('expected GoAST, got %r' % node.__class__.__name__)
    if indent is not None and not isinstance(indent, str):
        indent = ' ' * indent
    return _format(node)[0]

def dump_json(node, annotate_fields=True, include_attributes=False, *, indent=None):
    """
    Return a formatted dump of the tree in node. If annotate_fields is true (by default),
    the returned string will show the names and the values for fields.
    If annotate_fields is false, the result string will be more compact by
    omitting unambiguous field names.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    include_attributes can be set to true. If indent is a non-negative
    integer or string, then the tree will be pretty-printed with that indent
    level. None (the default) selects the single line representation.
    """

    def _format(node, level=0):
        if indent is not None:
            level += 1
        class_name = getattr(node, "_prefix", "") + node.__class__.__name__

        if isinstance(node, GoAST):
            node.remove_falsy_fields()
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
                    try:
                        json.dumps(value)
                        args.append({name: value})
                    except:
                        args.append({name: repr(value)})
                else:
                    try:
                        json.dumps(value)
                        args.append(value)
                    except:
                        args.append(repr(value))
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
                    try:
                        json.dumps(value)
                        args.append({name: value})
                    except:
                        args.append({name: repr(value)})
            if allsimple and len(args) <= 3:
                return {f"&{class_name}": args}, not args
            return {f"&{class_name}": args}, False
        elif isinstance(node, list):
            list_type = get_list_type(node)
            if not node:
                return {f'[]{list_type}': []}, True
            return {f"[]{list_type}": [_format(x, level)[0] for x in node]}, False
        return node, True

    if not isinstance(node, GoAST):
        raise TypeError('expected GoAST, got %r' % node.__class__.__name__)
    if indent is not None and not isinstance(indent, str):
        indent = ' ' * indent
    return json.dumps(_format(node)[0])


def clean_go_tree(go_tree: File):
    from pytago.go_ast import InterfaceTypeCounter
    start_count = 0
    end_count = -1
    repeats = -1
    while end_count < start_count:
        repeats += 1
        start_count = InterfaceTypeCounter.get_interface_count(go_tree)
        for tsfm in ALL_TRANSFORMS:
            if repeats == 0 or tsfm.REPEATABLE:
                tsfm().visit(go_tree)
        end_count = InterfaceTypeCounter.get_interface_count(go_tree)


def _gorun(filename: str) -> str:
    p = Popen(["go", "run", "-gcflags=-N -l", filename], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    out, err = p.communicate()
    if err:
        return "\n".join("// " + x for x in err.decode().strip().splitlines())
    return out.decode()


def _gofumpt(code: str) -> str:
    p = Popen(["gofumpt", "-s"], stdout=PIPE, stderr=PIPE, stdin=PIPE)
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
