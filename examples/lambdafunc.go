package main

import "fmt"

func main() {
	f := func(x int) int {
		return int(x) * 2
	}
	for a := 0; a < 10; a++ {
		fmt.Println(func(x int) int {
			return int(x) + 1
		}(a) + f(a))
	}
}
