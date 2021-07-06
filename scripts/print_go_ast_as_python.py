"""
Dirty script to help generate go_ast code from an actual Go AST.
Paste go code into https://lu4p.github.io/astextract/ and then the AST here.
"""

AST = r"""
&ast.CallExpr {
  Fun: &ast.FuncLit {
    Type: &ast.FuncType {
      Params: &ast.FieldList {
        List: []*ast.Field {
          &ast.Field {
            Names: []*ast.Ident {
              &ast.Ident {
                Name: "repeated",
              },
            },
            Type: &ast.ArrayType {
              Elt: &ast.Ident {
                Name: "int",
              },
            },
          },
          &ast.Field {
            Names: []*ast.Ident {
              &ast.Ident {
                Name: "n",
              },
            },
            Type: &ast.Ident {
              Name: "int",
            },
          },
        },
      },
      Results: &ast.FieldList {
        List: []*ast.Field {
          &ast.Field {
            Names: []*ast.Ident {
              &ast.Ident {
                Name: "result",
              },
            },
            Type: &ast.ArrayType {
              Elt: &ast.Ident {
                Name: "int",
              },
            },
          },
        },
      },
    },
    Body: &ast.BlockStmt {
      List: []ast.Stmt {
        &ast.ForStmt {
          Init: &ast.AssignStmt {
            Lhs: []ast.Expr {
              &ast.Ident {
                Name: "i",
              },
            },
            Tok: token.DEFINE,
            Rhs: []ast.Expr {
              &ast.BasicLit {
                Kind: token.INT,
                Value: "0",
              },
            },
          },
          Cond: &ast.BinaryExpr {
            X: &ast.Ident {
              Name: "i",
            },
            Op: token.LSS,
            Y: &ast.Ident {
              Name: "n",
            },
          },
          Post: &ast.IncDecStmt {
            X: &ast.Ident {
              Name: "i",
            },
            Tok: token.INC,
          },
          Body: &ast.BlockStmt {
            List: []ast.Stmt {
              &ast.AssignStmt {
                Lhs: []ast.Expr {
                  &ast.Ident {
                    Name: "result",
                  },
                },
                Tok: token.ASSIGN,
                Rhs: []ast.Expr {
                  &ast.CallExpr {
                    Fun: &ast.Ident {
                      Name: "append",
                    },
                    Args: []ast.Expr {
                      &ast.Ident {
                        Name: "result",
                      },
                      &ast.Ident {
                        Name: "repeated",
                      },
                    },
                    Ellipsis: 109,
                  },
                },
              },
            },
          },
        },
        &ast.ReturnStmt {
          Results: []ast.Expr {
            &ast.Ident {
              Name: "result",
            },
          },
        },
      },
    },
  },
  Args: []ast.Expr {
    &ast.Ident {
      Name: "elts",
    },
    &ast.Ident {
      Name: "number",
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
