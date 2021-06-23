package main

import "fmt"

func main() {
	x := []int{1, 2, 3, 4}
	for len(x) != 0 {
		fmt.Println(func() int {
			i := len(x) - 1
			popped := x[i]
			x = x[:i]
			return popped
		}())
	}
}