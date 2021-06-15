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
                Name: "a",
              },
            },
            Tok: token.DEFINE,
            Rhs: []ast.Expr {
              &ast.CompositeLit {
                Type: &ast.ArrayType {
                  Elt: &ast.Ident {
                    Name: "int",
                  },
                },
                Elts: []ast.Expr {
                  &ast.BasicLit {
                    Kind: token.INT,
                    Value: "1",
                  },
                  &ast.BasicLit {
                    Kind: token.INT,
                    Value: "2",
                  },
                  &ast.BasicLit {
                    Kind: token.INT,
                    Value: "3",
                  },
                },
              },
            },
          },
          &ast.ExprStmt {
            X: &ast.CallExpr {
              Fun: &ast.Ident {
                Name: "print",
              },
              Args: []ast.Expr {
                &ast.BinaryExpr {
                  X: &ast.CallExpr {
                    Fun: &ast.FuncLit {
                      Type: &ast.FuncType {
                        Params: &ast.FieldList {},
                        Results: &ast.FieldList {
                          List: []*ast.Field {
                            &ast.Field {
                              Type: &ast.Ident {
                                Name: "int",
                              },
                            },
                          },
                        },
                      },
                      Body: &ast.BlockStmt {
                        List: []ast.Stmt {
                          &ast.RangeStmt {
                            Key: &ast.Ident {
                              Name: "i",
                            },
                            Value: &ast.Ident {
                              Name: "v",
                            },
                            Tok: token.DEFINE,
                            X: &ast.Ident {
                              Name: "a",
                            },
                            Body: &ast.BlockStmt {
                              List: []ast.Stmt {
                                &ast.IfStmt {
                                  Cond: &ast.BinaryExpr {
                                    X: &ast.Ident {
                                      Name: "v",
                                    },
                                    Op: token.EQL,
                                    Y: &ast.BasicLit {
                                      Kind: token.INT,
                                      Value: "1",
                                    },
                                  },
                                  Body: &ast.BlockStmt {
                                    List: []ast.Stmt {
                                      &ast.ReturnStmt {
                                        Results: []ast.Expr {
                                          &ast.Ident {
                                            Name: "i",
                                          },
                                        },
                                      },
                                    },
                                  },
                                },
                              },
                            },
                          },
                          &ast.ReturnStmt {
                            Results: []ast.Expr {
                              &ast.UnaryExpr {
                                Op: token.SUB,
                                X: &ast.BasicLit {
                                  Kind: token.INT,
                                  Value: "1",
                                },
                              },
                            },
                          },
                        },
                      },
                    },
                  },
                  Op: token.NEQ,
                  Y: &ast.UnaryExpr {
                    Op: token.SUB,
                    X: &ast.BasicLit {
                      Kind: token.INT,
                      Value: "1",
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
