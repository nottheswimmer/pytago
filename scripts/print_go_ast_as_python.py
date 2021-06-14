"""
Dirty script to help generate go_ast code from an actual Go AST.
Paste go code into https://lu4p.github.io/astextract/ and then the AST here.
"""

AST = r"""
&ast.CallExpr {
  Fun: &ast.FuncLit {
    Type: &ast.FuncType {
      Params: &ast.FieldList {},
    },
    Body: &ast.BlockStmt {
      List: []ast.Stmt {
        &ast.IfStmt {
          Init: &ast.AssignStmt {
            Lhs: []ast.Expr {
              &ast.Ident {
                Name: "err",
              },
            },
            Tok: token.DEFINE,
            Rhs: []ast.Expr {
              &ast.CallExpr {
                Fun: &ast.SelectorExpr {
                  X: &ast.Ident {
                    Name: "f",
                  },
                  Sel: &ast.Ident {
                    Name: "Close",
                  },
                },
              },
            },
          },
          Cond: &ast.BinaryExpr {
            X: &ast.Ident {
              Name: "err",
            },
            Op: token.NEQ,
            Y: &ast.Ident {
              Name: "nil",
            },
          },
          Body: &ast.BlockStmt {
            List: []ast.Stmt {
              &ast.ExprStmt {
                X: &ast.CallExpr {
                  Fun: &ast.Ident {
                    Name: "panic",
                  },
                  Args: []ast.Expr {
                    &ast.Ident {
                      Name: "err",
                    },
                  },
                },
              },
            },
          },
        },
      },
    },
  },
}
"""

def go_ast_to_py(tree: str) -> str:
    result = ""
    list_closing_levels = []
    for line in tree.splitlines(keepends=True):
        level = len(line) - len(line.lstrip())
        before_quote, *after_quote = line.split('"')
        for a, b in {
            "&": "",
            ' {': '(',
            '}': ')',
            ': ': '=',
        }.items():
            before_quote = before_quote.replace(a, b)
        if not after_quote:
            before_quote, *after_list = before_quote.split("[]")
            if after_list:
                before_quote += '[' + '\n'
                list_closing_levels.append(level)
            elif level in list_closing_levels:
                before_quote = before_quote.replace(')', ']')
                list_closing_levels.remove(level)
        result += '"'.join([before_quote] + after_quote)
    return result

if __name__ == '__main__':
    print(go_ast_to_py(AST))
