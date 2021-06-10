package main

import "fmt"

func main() {
	a := 7
	b := add(a, -2)
	if a > b {
		fmt.Println("It's bigger")
	} else if a == b {
		fmt.Println("They're equal")
	} else {
		fmt.Println("It's smaller")
	}
}

func add(a int, b int) int {
	return a + b
}
