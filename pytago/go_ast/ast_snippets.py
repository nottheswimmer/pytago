from typing import List, Optional

import pytago.go_ast.core as ast


def fstring(template_str: str, key_value_elements=list['ast.KeyValueExpr']) -> 'ast.CallExpr':
    """
    func() string {
		var buf bytes.Buffer
		err := template.Must(template.New("f").Parse("I am {{.}}")).Execute(&buf, myvar)
		if err != nil {
			panic(err)
		}
		return buf.String()
	}()
    """
    token = ast.token
    return ast.CallExpr(
        Fun=ast.FuncLit(
            Type=ast.FuncType(
                Params=ast.FieldList(),
                Results=ast.FieldList(
                    List=[
                        ast.Field(
                            Type=ast.Ident(
                                Name="string",
                            ),
                        ),
                    ],
                ),
            ),
            Body=ast.BlockStmt(
                List=[
                    ast.DeclStmt(
                        Decl=ast.GenDecl(
                            Tok=token.VAR,
                            Specs=[
                                ast.ValueSpec(
                                    Names=[
                                        ast.Ident(
                                            Name="buf",
                                        ),
                                    ],
                                    Type=ast.SelectorExpr(
                                        X=ast.Ident(
                                            Name="bytes",
                                        ),
                                        Sel=ast.Ident(
                                            Name="Buffer",
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ast.AssignStmt(
                        Lhs=[
                            ast.Ident(
                                Name="err",
                            ),
                        ],
                        Tok=token.DEFINE,
                        Rhs=[
                            ast.CallExpr(
                                Fun=ast.SelectorExpr(
                                    X=ast.CallExpr(
                                        Fun=ast.SelectorExpr(
                                            X=ast.Ident(
                                                Name="template",
                                            ),
                                            Sel=ast.Ident(
                                                Name="Must",
                                            ),
                                        ),
                                        Args=[
                                            ast.CallExpr(
                                                Fun=ast.SelectorExpr(
                                                    X=ast.CallExpr(
                                                        Fun=ast.SelectorExpr(
                                                            X=ast.Ident(
                                                                Name="template",
                                                            ),
                                                            Sel=ast.Ident(
                                                                Name="New",
                                                            ),
                                                        ),
                                                        Args=[
                                                            ast.BasicLit(
                                                                Kind=token.STRING,
                                                                Value="f",
                                                            ),
                                                        ],
                                                    ),
                                                    Sel=ast.Ident(
                                                        Name="Parse",
                                                    ),
                                                ),
                                                Args=[
                                                    ast.BasicLit(
                                                        Kind=token.STRING,
                                                        Value=template_str,
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    Sel=ast.Ident(
                                        Name="Execute",
                                    ),
                                ),
                                Args=[
                                    ast.UnaryExpr(
                                        Op=token.AND,
                                        X=ast.Ident(
                                            Name="buf",
                                        ),
                                    ),
                                    ast.CompositeLit(
                                        Type=ast.MapType(
                                            Key=ast.Ident(
                                                Name="string",
                                            ),
                                            Value=ast.InterfaceType(
                                                Methods=ast.FieldList(),
                                            ),
                                        ),
                                        Elts=key_value_elements,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    ast.IfStmt(
                        Cond=ast.BinaryExpr(
                            X=ast.Ident(
                                Name="err",
                            ),
                            Op=token.NEQ,
                            Y=ast.Ident(
                                Name="nil",
                            ),
                        ),
                        Body=ast.BlockStmt(
                            List=[
                                ast.ExprStmt(
                                    X=ast.CallExpr(
                                        Fun=ast.Ident(
                                            Name="panic",
                                        ),
                                        Args=[
                                            ast.Ident(
                                                Name="err",
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ast.ReturnStmt(
                        Results=[
                            ast.CallExpr(
                                Fun=ast.SelectorExpr(
                                    X=ast.Ident(
                                        Name="buf",
                                    ),
                                    Sel=ast.Ident(
                                        Name="String",
                                    ),
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ),
    )


def wrap_err(err: 'ast.Expr'):
    token = ast.token
    return ast.CallExpr(
        Fun=ast.FuncLit(
            Type=ast.FuncType(
                Params=ast.FieldList(),
            ),
            Body=ast.BlockStmt(
                List=[
                    ast.IfStmt(
                        Init=ast.AssignStmt(
                            Lhs=[
                                ast.Ident(
                                    Name="err",
                                ),
                            ],
                            Tok=token.DEFINE,
                            Rhs=[
                                err,
                            ]
                        ),
                        Cond=ast.BinaryExpr(
                            X=ast.Ident(
                                Name="err",
                            ),
                            Op=token.NEQ,
                            Y=ast.Ident(
                                Name="nil",
                            ),
                        ),
                        Body=ast.BlockStmt(
                            List=[
                                ast.ExprStmt(
                                    X=ast.CallExpr(
                                        Fun=ast.Ident(
                                            Name="panic",
                                        ),
                                        Args=[
                                            ast.Ident(
                                                Name="err",
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ),
    )


def index(iterable: 'ast.Expr', element: 'ast.Expr'):
    token = ast.token
    return ast.CallExpr(
        Fun=ast.FuncLit(
            Type=ast.FuncType(
                Params=ast.FieldList(),
                Results=ast.FieldList(
                    List=[
                        ast.Field(
                            Type=ast.Ident(
                                Name="int",
                            ),
                        ),
                    ],
                ),
            ),
            Body=ast.BlockStmt(
                List=[
                    ast.RangeStmt(
                        Key=ast.Ident(
                            Name="i",
                        ),
                        Value=ast.Ident(
                            Name="v",  # TODO: Deal with potential naming conflicts
                        ),
                        Tok=token.DEFINE,
                        X=iterable,
                        Body=ast.BlockStmt(
                            List=[
                                ast.IfStmt(
                                    Cond=ast.BinaryExpr(
                                        X=ast.Ident(
                                            Name="v",
                                        ),
                                        Op=token.EQL,
                                        # TODO: Performance will take a hit if this something expensive like a function call
                                        #  Easy fix is to store it to a variable inside the function in such cases
                                        #  Passing it in is more annoying because it means I have to deal w/ types
                                        Y=element,
                                    ),
                                    Body=ast.BlockStmt(
                                        List=[
                                            ast.ReturnStmt(
                                                Results=[
                                                    ast.Ident(
                                                        Name="i",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ast.ReturnStmt(
                        Results=[
                            ast.UnaryExpr(
                                Op=token.SUB,
                                X=ast.BasicLit(Kind=token.INT, Value=1),
                            ),
                        ],
                    ),
                ],
            ),
        ),
    )

def handler_name_to_cond(name: str) -> 'ast.Expr':
    token = ast.token
    cond = ast.CallExpr(
                Fun=ast.SelectorExpr(
                    X=ast.Ident(
                        Name="strings",
                    ),
                    Sel=ast.Ident(
                        Name="HasPrefix",
                    ),
                ),
                Args=[
                    ast.CallExpr(
                        Fun=ast.SelectorExpr(
                            X=ast.Ident(
                                Name="err",
                            ),
                            Sel=ast.Ident(
                                Name="Error",
                            ),
                        ),
                    ),
                    ast.BasicLit(
                        Kind=token.STRING,
                        Value=name,
                    ),
                ],
            )
    # Add support for some built-in go error handling where possible
    if name == "IndexError":
        cond = cond.or_(handler_name_to_cond("runtime error: index out of range"))
    elif name == "RuntimeError":
        cond = cond.or_(handler_name_to_cond("runtime error"))
    return cond

def exceptions(conditional: list[tuple['ast.Expr', list['ast.Stmt']]], base: list['ast.Stmt'],
               conditional_names: list[Optional['ast.Ident']], base_name: Optional['ast.Ident']):
    token = ast.token
    body = []
    conditional.reverse()
    conditional_names.reverse()
    used_err = False
    while conditional:
        used_err = True
        exception_cond, exception_body = conditional.pop()
        name = conditional_names.pop()
        name_declarations = []
        if name:
            name_declarations.append(ast.AssignStmt(Lhs=[name],
                                                    Tok=token.DEFINE,
                                                    Rhs=[ast.Ident.from_str("err")]))
        if_stmt = ast.IfStmt(
            Cond=exception_cond,
            Body=ast.BlockStmt(
                List=[
                    *name_declarations,
                    *exception_body,
                    ast.ReturnStmt(),
                ],
            )
        )
        if not body:
            body.append(if_stmt)
        else:
            last_if = body[-1]
            while last_if.Else:
                last_if = last_if.Else
            last_if.Else = if_stmt
    if base:
        name_declarations = []
        if base_name:
            name_declarations.append(ast.AssignStmt(Lhs=[base_name],
                                                    Tok=token.DEFINE,
                                                    Rhs=[ast.Ident.from_str("err")]))
            used_err = True
        base_stmts = [*name_declarations, *base, ast.ReturnStmt()]
        if body:
            last_if = body[-1]
            while last_if.Else:
                last_if = last_if.Else
            last_if.Else = ast.BlockStmt(List=base_stmts)
        else:
            body += base_stmts

    return ast.DeferStmt(
        Call=ast.CallExpr(
            Fun=ast.FuncLit(
                Type=ast.FuncType(
                    Params=ast.FieldList(),
                ),
                Body=ast.BlockStmt(
                    List=[
                        # TODO: try / else support would be tacked on as an else clause here
                        ast.IfStmt(
                            Init=ast.AssignStmt(
                                Lhs=[
                                    ast.Ident(
                                        Name="r",
                                    ),
                                ],
                                Tok=token.DEFINE,
                                Rhs=[
                                    ast.CallExpr(
                                        Fun=ast.Ident(
                                            Name="recover",
                                        ),
                                    ),
                                ],
                            ),
                            Cond=ast.BinaryExpr(
                                X=ast.Ident(
                                    Name="r",
                                ),
                                Op=token.NEQ,
                                Y=ast.Ident(
                                    Name="nil",
                                ),
                            ),
                            Body=ast.BlockStmt(
                                List=[
                                    ast.IfStmt(
                                        Init=ast.AssignStmt(
                                            Lhs=[
                                                ast.Ident(
                                                    Name="err" if used_err else "_",
                                                ),
                                                ast.Ident(
                                                    Name="ok",
                                                ),
                                            ],
                                            Tok=token.DEFINE,
                                            Rhs=[
                                                ast.TypeAssertExpr(
                                                    X=ast.Ident(
                                                        Name="r",
                                                    ),
                                                    Type=ast.Ident(
                                                        Name="error",
                                                    ),
                                                ),
                                            ],
                                        ),
                                        Cond=ast.Ident(
                                            Name="ok",
                                        ),
                                        Body=ast.BlockStmt(
                                            List=body,
                                        ),
                                    ),
                                    ast.ExprStmt(
                                        X=ast.CallExpr(
                                            Fun=ast.Ident(
                                                Name="panic",
                                            ),
                                            Args=[
                                                ast.Ident(
                                                    Name="r",
                                                ),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        ),
    )
