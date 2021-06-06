package main

import "fmt"

func main() {
	a := "hello"
	b := "world"
	c := a + " " + b
	fmt.Println(c)
	fmt.Println(double_it(c))
	fmt.Println(string(c[1]))
	fmt.Println(c[1:6])
}
func double_it(c string) string {
	return c + c
}
