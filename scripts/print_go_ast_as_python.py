"""
Dirty script to help generate go_ast code from an actual Go AST.
Paste go code into https://lu4p.github.io/astextract/ and then the AST here.
"""

AST = r"""
&ast.File {
  Package: 1,
  Name: &ast.Ident {
    Name: "main",
  },
  Decls: []ast.Decl {
    &ast.GenDecl {
      Tok: token.IMPORT,
      Specs: []ast.Spec {
        &ast.ImportSpec {
          Path: &ast.BasicLit {
            Kind: token.STRING,
            Value: "\"fmt\"",
          },
        },
      },
    },
    &ast.FuncDecl {
      Name: &ast.Ident {
        Name: "main",
      },
      Type: &ast.FuncType {
        Params: &ast.FieldList {},
      },
      Body: &ast.BlockStmt {
        List: []ast.Stmt {
          &ast.AssignStmt {
            Lhs: []ast.Expr {
              &ast.Ident {
                Name: "x",
              },
            },
            Tok: token.DEFINE,
            Rhs: []ast.Expr {
              &ast.CompositeLit {
                Type: &ast.MapType {
                  Key: &ast.InterfaceType {
                    Methods: &ast.FieldList {},
                  },
                  Value: &ast.InterfaceType {
                    Methods: &ast.FieldList {},
                  },
                },
                Elts: []ast.Expr {
                  &ast.KeyValueExpr {
                    Key: &ast.BasicLit {
                      Kind: token.STRING,
                      Value: "\"a\"",
                    },
                    Value: &ast.BasicLit {
                      Kind: token.INT,
                      Value: "123",
                    },
                  },
                },
              },
            },
          },
          &ast.ExprStmt {
            X: &ast.CallExpr {
              Fun: &ast.SelectorExpr {
                X: &ast.Ident {
                  Name: "fmt",
                },
                Sel: &ast.Ident {
                  Name: "Println",
                },
              },
              Args: []ast.Expr {
                &ast.IndexExpr {
                  X: &ast.Ident {
                    Name: "x",
                  },
                  Index: &ast.BasicLit {
                    Kind: token.STRING,
                    Value: "\"a\"",
                  },
                },
              },
            },
          },
          &ast.ExprStmt {
            X: &ast.CallExpr {
              Fun: &ast.SelectorExpr {
                X: &ast.Ident {
                  Name: "fmt",
                },
                Sel: &ast.Ident {
                  Name: "Println",
                },
              },
              Args: []ast.Expr {
                &ast.Ident {
                  Name: "x",
                },
              },
            },
          },
        },
      },
    },
  },
  Imports: []*ast.ImportSpec {
    &ast.ImportSpec {
      Path: &ast.BasicLit {
        Kind: token.STRING,
        Value: "\"fmt\"",
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
