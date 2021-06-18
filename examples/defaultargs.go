package main

import "fmt"

func main() {
	a := increment(1, 1, false)
	fmt.Println(a)
	b := increment(a, 2, false)
	fmt.Println(b)
	c := increment(a, 3, true)
	fmt.Println(c)
}

func increment(n int, amount int, decrement bool) int {
	if decrement {
		return n - amount
	}
	return n + amount
}
