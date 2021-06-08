import pythagoras.go_ast.core as ast


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
    # key_value_elements = [
    #     ast.KeyValueExpr(
    #         Key=ast.BasicLit(
    #             Kind=token.STRING,
    #             Value="\"myvar\"",
    #         ),
    #         Value=ast.Ident(
    #             Name="myvar",
    #         ),
    #     ),
    # ]
    # template_string = "\"I am {{.myvar}}\""
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