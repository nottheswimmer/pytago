import os
import uuid
from subprocess import Popen, PIPE

from pythagoras.go_ast import dump, GoAST, ALL_TRANSFORMS, FuncDecl, File


def unparse(go_tree: GoAST):
    clean_go_tree(go_tree)
    # XXX: Probably vulnerable to RCE if you put this on a server.
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
    if tmp_file not in code:
        os.remove(tmp_file)
    return _gofmt(_goimport(code))


def clean_go_tree(go_tree: File):
    # Remove orphaned code left in functions titled "_"
    to_delete = []
    for decl in go_tree.Decls:
        if isinstance(decl, FuncDecl) and decl.Name.Name == '_':
            to_delete.append(decl)
    for decl in to_delete:
        go_tree.Decls.remove(decl)

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
