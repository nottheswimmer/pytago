import os
import uuid
from subprocess import Popen, PIPE

from pythagoras.go_ast import dump, GoAST, ALL_TRANSFORMS, FuncDecl, File


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
