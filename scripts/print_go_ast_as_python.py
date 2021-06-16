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
        &ast.ImportSpec {
          Path: &ast.BasicLit {
            Kind: token.STRING,
            Value: "\"strings\"",
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
          &ast.DeferStmt {
            Call: &ast.CallExpr {
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
                            Name: "r",
                          },
                        },
                        Tok: token.DEFINE,
                        Rhs: []ast.Expr {
                          &ast.CallExpr {
                            Fun: &ast.Ident {
                              Name: "recover",
                            },
                          },
                        },
                      },
                      Cond: &ast.BinaryExpr {
                        X: &ast.Ident {
                          Name: "r",
                        },
                        Op: token.NEQ,
                        Y: &ast.Ident {
                          Name: "nil",
                        },
                      },
                      Body: &ast.BlockStmt {
                        List: []ast.Stmt {
                          &ast.IfStmt {
                            Init: &ast.AssignStmt {
                              Lhs: []ast.Expr {
                                &ast.Ident {
                                  Name: "err",
                                },
                                &ast.Ident {
                                  Name: "ok",
                                },
                              },
                              Tok: token.DEFINE,
                              Rhs: []ast.Expr {
                                &ast.TypeAssertExpr {
                                  X: &ast.Ident {
                                    Name: "r",
                                  },
                                  Type: &ast.Ident {
                                    Name: "error",
                                  },
                                },
                              },
                            },
                            Cond: &ast.Ident {
                              Name: "ok",
                            },
                            Body: &ast.BlockStmt {
                              List: []ast.Stmt {
                                &ast.IfStmt {
                                  Cond: &ast.CallExpr {
                                    Fun: &ast.SelectorExpr {
                                      X: &ast.Ident {
                                        Name: "strings",
                                      },
                                      Sel: &ast.Ident {
                                        Name: "HasPrefix",
                                      },
                                    },
                                    Args: []ast.Expr {
                                      &ast.CallExpr {
                                        Fun: &ast.SelectorExpr {
                                          X: &ast.Ident {
                                            Name: "err",
                                          },
                                          Sel: &ast.Ident {
                                            Name: "Error",
                                          },
                                        },
                                      },
                                      &ast.BasicLit {
                                        Kind: token.STRING,
                                        Value: "\"Handler 1 case goes here\"",
                                      },
                                    },
                                  },
                                  Body: &ast.BlockStmt {
                                    List: []ast.Stmt {
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
                                            &ast.BasicLit {
                                              Kind: token.STRING,
                                              Value: "\"Handler 1 body goes here\"",
                                            },
                                          },
                                        },
                                      },
                                      &ast.ReturnStmt {},
                                    },
                                  },
                                  Else: &ast.IfStmt {
                                    Cond: &ast.CallExpr {
                                      Fun: &ast.SelectorExpr {
                                        X: &ast.Ident {
                                          Name: "strings",
                                        },
                                        Sel: &ast.Ident {
                                          Name: "HasPrefix",
                                        },
                                      },
                                      Args: []ast.Expr {
                                        &ast.CallExpr {
                                          Fun: &ast.SelectorExpr {
                                            X: &ast.Ident {
                                              Name: "err",
                                            },
                                            Sel: &ast.Ident {
                                              Name: "Error",
                                            },
                                          },
                                        },
                                        &ast.BasicLit {
                                          Kind: token.STRING,
                                          Value: "\"Handler N case goes here\"",
                                        },
                                      },
                                    },
                                    Body: &ast.BlockStmt {
                                      List: []ast.Stmt {
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
                                              &ast.BasicLit {
                                                Kind: token.STRING,
                                                Value: "\"Handler N body goes here\"",
                                              },
                                            },
                                          },
                                        },
                                        &ast.ReturnStmt {},
                                      },
                                    },
                                    Else: &ast.BlockStmt {
                                      List: []ast.Stmt {
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
                                              &ast.BasicLit {
                                                Kind: token.STRING,
                                                Value: "\"Exception / BaseException / bare 'except' case goes here\"",
                                              },
                                            },
                                          },
                                        },
                                        &ast.ReturnStmt {},
                                      },
                                    },
                                  },
                                },
                              },
                            },
                          },
                          &ast.ExprStmt {
                            X: &ast.CallExpr {
                              Fun: &ast.Ident {
                                Name: "panic",
                              },
                              Args: []ast.Expr {
                                &ast.Ident {
                                  Name: "r",
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
    &ast.ImportSpec {
      Path: &ast.BasicLit {
        Kind: token.STRING,
        Value: "\"strings\"",
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
