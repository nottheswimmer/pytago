package main

import (
	"bytes"
	"fmt"
	"text/template"
)

func main() {
	name := "Michael"
	age := 24
	fmt.Println(func() string {
		var buf bytes.Buffer
		err := template.Must(template.New("f").Parse("My name is {{.name}} and I am {{.age}} years old. Later this year I'll be {{.expr1}}!")).
			Execute(&buf, map[string]interface{}{"name": name, "age": age, "expr1": age + 1})
		if err != nil {
			panic(err)
		}
		return buf.String()
	}())
}
