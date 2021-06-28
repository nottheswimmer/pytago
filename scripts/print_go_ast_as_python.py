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
            Value: "\"bufio\"",
          },
        },
        &ast.ImportSpec {
          Path: &ast.BasicLit {
            Kind: token.STRING,
            Value: "\"fmt\"",
          },
        },
        &ast.ImportSpec {
          Path: &ast.BasicLit {
            Kind: token.STRING,
            Value: "\"os\"",
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
                Name: "fh",
              },
            },
            Tok: token.DEFINE,
            Rhs: []ast.Expr {
              &ast.CallExpr {
                Fun: &ast.FuncLit {
                  Type: &ast.FuncType {
                    Params: &ast.FieldList {},
                    Results: &ast.FieldList {
                      List: []*ast.Field {
                        &ast.Field {
                          Type: &ast.StarExpr {
                            X: &ast.SelectorExpr {
                              X: &ast.Ident {
                                Name: "os",
                              },
                              Sel: &ast.Ident {
                                Name: "File",
                              },
                            },
                          },
                        },
                      },
                    },
                  },
                  Body: &ast.BlockStmt {
                    List: []ast.Stmt {
                      &ast.AssignStmt {
                        Lhs: []ast.Expr {
                          &ast.Ident {
                            Name: "f",
                          },
                          &ast.Ident {
                            Name: "err",
                          },
                        },
                        Tok: token.DEFINE,
                        Rhs: []ast.Expr {
                          &ast.CallExpr {
                            Fun: &ast.SelectorExpr {
                              X: &ast.Ident {
                                Name: "os",
                              },
                              Sel: &ast.Ident {
                                Name: "OpenFile",
                              },
                            },
                            Args: []ast.Expr {
                              &ast.BasicLit {
                                Kind: token.STRING,
                                Value: "\"file.txt\"",
                              },
                              &ast.SelectorExpr {
                                X: &ast.Ident {
                                  Name: "os",
                                },
                                Sel: &ast.Ident {
                                  Name: "O_RDONLY",
                                },
                              },
                              &ast.BasicLit {
                                Kind: token.INT,
                                Value: "0o777",
                              },
                            },
                          },
                        },
                      },
                      &ast.IfStmt {
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
                      &ast.ReturnStmt {
                        Results: []ast.Expr {
                          &ast.Ident {
                            Name: "f",
                          },
                        },
                      },
                    },
                  },
                },
              },
            },
          },
          &ast.IfStmt {
            Init: &ast.AssignStmt {
              Lhs: []ast.Expr {
                &ast.Ident {
                  Name: "sc",
                },
              },
              Tok: token.DEFINE,
              Rhs: []ast.Expr {
                &ast.CallExpr {
                  Fun: &ast.SelectorExpr {
                    X: &ast.Ident {
                      Name: "bufio",
                    },
                    Sel: &ast.Ident {
                      Name: "NewScanner",
                    },
                  },
                  Args: []ast.Expr {
                    &ast.Ident {
                      Name: "fh",
                    },
                  },
                },
              },
            },
            Cond: &ast.CallExpr {
              Fun: &ast.SelectorExpr {
                X: &ast.Ident {
                  Name: "sc",
                },
                Sel: &ast.Ident {
                  Name: "Scan",
                },
              },
            },
            Body: &ast.BlockStmt {
              List: []ast.Stmt {
                &ast.ForStmt {
                  Init: &ast.AssignStmt {
                    Lhs: []ast.Expr {
                      &ast.Ident {
                        Name: "line",
                      },
                      &ast.Ident {
                        Name: "more",
                      },
                      &ast.Ident {
                        Name: "done",
                      },
                    },
                    Tok: token.DEFINE,
                    Rhs: []ast.Expr {
                      &ast.CallExpr {
                        Fun: &ast.SelectorExpr {
                          X: &ast.Ident {
                            Name: "sc",
                          },
                          Sel: &ast.Ident {
                            Name: "Text",
                          },
                        },
                      },
                      &ast.CallExpr {
                        Fun: &ast.SelectorExpr {
                          X: &ast.Ident {
                            Name: "sc",
                          },
                          Sel: &ast.Ident {
                            Name: "Scan",
                          },
                        },
                      },
                      &ast.Ident {
                        Name: "false",
                      },
                    },
                  },
                  Cond: &ast.UnaryExpr {
                    Op: token.NOT,
                    X: &ast.Ident {
                      Name: "done",
                    },
                  },
                  Post: &ast.AssignStmt {
                    Lhs: []ast.Expr {
                      &ast.Ident {
                        Name: "line",
                      },
                      &ast.Ident {
                        Name: "more",
                      },
                      &ast.Ident {
                        Name: "done",
                      },
                    },
                    Tok: token.ASSIGN,
                    Rhs: []ast.Expr {
                      &ast.CallExpr {
                        Fun: &ast.SelectorExpr {
                          X: &ast.Ident {
                            Name: "sc",
                          },
                          Sel: &ast.Ident {
                            Name: "Text",
                          },
                        },
                      },
                      &ast.CallExpr {
                        Fun: &ast.SelectorExpr {
                          X: &ast.Ident {
                            Name: "sc",
                          },
                          Sel: &ast.Ident {
                            Name: "Scan",
                          },
                        },
                      },
                      &ast.UnaryExpr {
                        Op: token.NOT,
                        X: &ast.Ident {
                          Name: "more",
                        },
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
                            &ast.Ident {
                              Name: "line",
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
          &ast.ExprStmt {
            X: &ast.CallExpr {
              Fun: &ast.FuncLit {
                Type: &ast.FuncType {
                  Params: &ast.FieldList {
                    List: []*ast.Field {
                      &ast.Field {
                        Names: []*ast.Ident {
                          &ast.Ident {
                            Name: "obj",
                          },
                        },
                        Type: &ast.StarExpr {
                          X: &ast.SelectorExpr {
                            X: &ast.Ident {
                              Name: "os",
                            },
                            Sel: &ast.Ident {
                              Name: "File",
                            },
                          },
                        },
                      },
                    },
                  },
                },
                Body: &ast.BlockStmt {
                  List: []ast.Stmt {
                    &ast.AssignStmt {
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
                              Name: "obj",
                            },
                            Sel: &ast.Ident {
                              Name: "Close",
                            },
                          },
                        },
                      },
                    },
                    &ast.IfStmt {
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
              Args: []ast.Expr {
                &ast.Ident {
                  Name: "fh",
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
        Value: "\"bufio\"",
      },
    },
    &ast.ImportSpec {
      Path: &ast.BasicLit {
        Kind: token.STRING,
        Value: "\"fmt\"",
      },
    },
    &ast.ImportSpec {
      Path: &ast.BasicLit {
        Kind: token.STRING,
        Value: "\"os\"",
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
