package main

import "fmt"

func main() {
	a := 3
	b := 7
	a = a + b
	fmt.Println(a + b)
	another_scope()
}

func another_scope() {
	a := 1
	b := 12
	a = a + b
	fmt.Println(a + b)
}
