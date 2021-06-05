package main

import "fmt"

func main() {
	a := true
	b := false
	fmt.Println(a)
	fmt.Println(b)
	fmt.Println(a && b)
	fmt.Println(a || b)
	fmt.Println(!a)
	fmt.Println(!b)
	fmt.Println(a && !b)
	fmt.Println(a || !b)
}
