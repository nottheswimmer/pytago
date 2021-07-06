package main

import "fmt"

func fib(n int) {
	a, b := 0, 1
	for a < int(n) {
		fmt.Print(a, " ")
		a, b = b, a+b
	}
	fmt.Println()
}

func main() {
	fib(1000)
	fmt.Print("All done!")
}
